import json
import os
import logging
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from fake_headers import Headers

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TWITTER_LOGIN_URL = "https://twitter.com/i/flow/login"

class Tweet:
    def __init__(self, card, driver, username=None, is_hashtag=False):
        self.tweet = None
        self.error = False
        try:
            handle = card.find_element("xpath", ".//span[starts-with(text(), '@')]").text
            content = card.find_element("xpath", ".//div[@data-testid='tweetText']").text
            # Collect all tweets for hashtag scraping, or filter by username for profile scraping
            if is_hashtag or (handle == f"@{username}" and content):
                self.tweet = {
                    "content": content,
                    "handle": handle,
                    "timestamp": card.find_element("xpath", ".//time").get_attribute("datetime"),
                    "tweet_id": card.find_element("xpath", ".//a[@href]").get_attribute("href").split("/")[-1]
                }
            else:
                self.error = True
        except (NoSuchElementException, StaleElementReferenceException):
            self.error = True
            logging.error("Error extracting tweet data")

class TwitterScraper:
    _instance = None

    @classmethod
    def get_instance(cls, mail=None, username=None, password=None):
        """
        Get the singleton instance of TwitterScraper, creating it if necessary.
        """
        if cls._instance is None:
            if not all([mail, username, password]):
                raise ValueError("Missing Twitter credentials for scraper initialization")
            cls._instance = cls(mail, username, password)
        return cls._instance

    def __init__(self, mail, username, password):
        """
        Initialize the scraper with credentials and log in to Twitter.
        Raises RuntimeError if called directly instead of using get_instance().
        """
        if self._instance is not None:
            raise RuntimeError("Use get_instance() to get the TwitterScraper instance")
        self.mail = mail
        self.username = username
        self.password = password
        self.tweet_ids = set()
        self.data = []
        self.driver = self._get_driver()
        self.login()

    def _get_driver(self):
        logging.info("Setting up WebDriver")
        header = Headers().generate()["User-Agent"]
        options = FirefoxOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(f"--user-agent={header}")

        gecko_path = "/home/kartik/Desktop/Analytica 2.0/Analytica/twitter_app/geckodriver"
        if os.path.exists(gecko_path):
            service = FirefoxService(executable_path=gecko_path)
            logging.info("Using local geckodriver")
        else:
            service = FirefoxService(executable_path=GeckoDriverManager().install())
            logging.info("Using geckodriver from GeckoDriverManager")

        driver = webdriver.Firefox(service=service, options=options)
        logging.info("WebDriver setup complete")
        return driver

    def login(self):
        logging.info("Logging in to Twitter...")
        self.driver.get(TWITTER_LOGIN_URL)
        sleep(3)
        try:
            username_field = self.driver.find_element("xpath", "//input[@autocomplete='username']")
            username_field.send_keys(self.username)
            username_field.send_keys(Keys.RETURN)
            sleep(3)
            password_field = self.driver.find_element("xpath", "//input[@autocomplete='current-password']")
            password_field.send_keys(self.password)
            password_field.send_keys(Keys.RETURN)
            sleep(3)
            logging.info("Login Successful")
        except Exception as e:
            logging.info(f"Login Failed: {e}")
            self.driver.quit()

    def go_to_profile(self, username):
        logging.info(f"Navigating to profile: {username}")
        self.driver.get(f"https://twitter.com/{username}")
        sleep(1.5)

    def go_to_hashtag(self, hashtag, latest=True):
        logging.info(f"Navigating to hashtag: {hashtag}")
        url = f"https://twitter.com/hashtag/{hashtag}?src=hashtag_click" + ("&f=live" if latest else "")
        self.driver.get(url)
        sleep(1.5)

    def scrape_tweets(self, max_tweets=50, scrape_username=None, scrape_hashtag=None, scrape_latest=True):
        logging.info("Starting tweet scraping")
        self.tweet_ids.clear()
        self.data.clear()

        if scrape_username:
            self.go_to_profile(scrape_username)
        elif scrape_hashtag:
            self.go_to_hashtag(scrape_hashtag, scrape_latest)
        else:
            logging.warning("No scrape target specified")
            return []

        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        max_scroll_attempts = 5

        while len(self.data) < max_tweets and scroll_attempts < max_scroll_attempts:
            tweet_cards = self.driver.find_elements("xpath", '//article[@data-testid="tweet"]')
            new_tweets_added = False

            for card in tweet_cards[-20:]:
                tweet_id = str(hash(card))
                if tweet_id not in self.tweet_ids:
                    self.tweet_ids.add(tweet_id)
                    # Pass is_hashtag=True for hashtag scraping
                    tweet = Tweet(card, self.driver, scrape_username, is_hashtag=bool(scrape_hashtag))
                    if not tweet.error and tweet.tweet:
                        self.data.append(tweet.tweet)
                        new_tweets_added = True
                        if len(self.data) >= max_tweets:
                            break

            if len(self.data) >= max_tweets:
                break

            self.driver.execute_script("window.scrollBy(0, 2000);")
            sleep(1.5)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height and not new_tweets_added:
                scroll_attempts += 1
                logging.info(f"No new tweets, attempt {scroll_attempts}/{max_scroll_attempts}")
            else:
                scroll_attempts = 0
                last_height = new_height

        logging.info(f"Scraped {len(self.data)} tweets")
        print(self.data)
        return self.data  # Return list of dictionaries instead of JSON

    def quit(self):
        logging.info("Quitting WebDriver")
        self.driver.quit()