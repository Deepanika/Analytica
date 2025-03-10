from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status
from .models import Tweet
from .serializers import TweetSerializer
from .scraper import TwitterScraper
from .analyzer import analyzer
from dotenv import load_dotenv
import os
import logging
from django.db.models import Q
# Configure logging
logger = logging.getLogger(__name__)

# Initialize the shared scraper instance as a singleton at module level
load_dotenv()
SCAPER = TwitterScraper.get_instance(
    mail=os.getenv("TWITTER_MAIL"),
    username=os.getenv("TWITTER_USERNAME"),
    password=os.getenv("TWITTER_PASSWORD")
)
logger.info("Scraper initialized and logged in")

def index(request):
    return render(request, "index.html")

# Homepage view
def homepage(request):
    """
    Render the homepage with links to all analysis functionalities.
    """
    return render(request, "homepage.html")

# Base viewset for common functionality
class BaseTweetViewSet(viewsets.ModelViewSet):
    """
    Base viewset providing common methods for tweet handling.
    """
    queryset = Tweet.objects.all()
    serializer_class = TweetSerializer

    @classmethod
    def get_scraper(cls):
        """
        Retrieve the singleton scraper instance.
        Reinitializes if the session is no longer connectable.
        """
        global SCAPER
        if not SCAPER.driver.service.is_connectable():
            logger.warning("Scraper session expired, reinitializing...")
            SCAPER.quit()
            SCAPER = TwitterScraper.get_instance(
                mail=os.getenv("TWITTER_MAIL"),
                username=os.getenv("TWITTER_USERNAME"),
                password=os.getenv("TWITTER_PASSWORD")
            )
        return SCAPER

    def save_tweets_to_db(self, tweets_data):
        """
        Save scraped tweets to the database and return the Tweet objects.
        """
        tweets = []
        for tweet_dict in tweets_data:
            tweet, created = Tweet.objects.get_or_create(
                tweet_id_name=f"{tweet_dict['tweet_id']}_{tweet_dict['timestamp']}",
                defaults={
                    "handle": tweet_dict["handle"],
                    "content": tweet_dict["content"],
                    "timestamp": tweet_dict["timestamp"],
                },
            )
            tweets.append(tweet)
        return tweets

# Sentiment Analysis ViewSet
class SentimentViewSet(BaseTweetViewSet):
    """
    ViewSet for handling sentiment analysis of tweets.
    """
    @action(detail=False, methods=["post"])
    def scrape(self, request):
        """
        Scrape and analyze tweets for sentiment.
        """
        try:
            # Validate input
            username = request.data.get("username")
            hashtag = request.data.get("hashtag")
            max_tweets = int(request.data.get("max_tweets", 50))
            targets = [t for t in [username, hashtag] if t]
            if len(targets) != 1:
                return Response({"error": "Enter either username or hashtag, not both"}, status=400)

            # Get scraper instance
            scraper = self.get_scraper()

            # Scrape tweets
            tweets_data = scraper.scrape_tweets(
                max_tweets=max_tweets, scrape_username=username, scrape_hashtag=hashtag
            )
            if not tweets_data:
                return Response({"message": "No tweets found"}, status=200)

            # Save to database and analyze
            tweets = self.save_tweets_to_db(tweets_data)
            analyzed_tweets = []
            for tweet in tweets:
                analyzed_tweet = analyzer.analyze(tweet, "sentiment")
                analyzed_tweets.append(TweetSerializer(analyzed_tweet).data)

            return Response(analyzed_tweets)
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return Response({"error": str(e)}, status=500)

def sentiment_page(request):
    """
    Render the sentiment analysis webpage.
    """
    return render(request, "sentiment.html")

# Toxicity Analysis ViewSet
class ToxicityViewSet(BaseTweetViewSet):
    """
    ViewSet for handling toxicity analysis of tweets.
    """
    @action(detail=False, methods=["post"])
    def scrape(self, request):
        """
        Scrape and analyze tweets for toxicity.
        """
        try:
            # Validate input
            username = request.data.get("username")
            hashtag = request.data.get("hashtag")
            max_tweets = int(request.data.get("max_tweets", 50))
            targets = [t for t in [username, hashtag] if t]
            if len(targets) != 1:
                return Response({"error": "Enter either username or hashtag, not both"}, status=400)

            # Get scraper instance
            scraper = self.get_scraper()

            # Scrape tweets
            tweets_data = scraper.scrape_tweets(
                max_tweets=max_tweets, scrape_username=username, scrape_hashtag=hashtag
            )
            if not tweets_data:
                return Response({"message": "No tweets found"}, status=200)

            # Save to database and analyze
            tweets = self.save_tweets_to_db(tweets_data)
            analyzed_tweets = []
            for tweet in tweets:
                analyzed_tweet = analyzer.analyze(tweet, "toxicity")
                analyzed_tweets.append(TweetSerializer(analyzed_tweet).data)

            return Response(analyzed_tweets)
        except Exception as e:
            logger.error(f"Error in toxicity analysis: {e}")
            return Response({"error": str(e)}, status=500)

def toxicity_page(request):
    """
    Render the toxicity analysis webpage.
    """
    return render(request, "toxicity.html")

# Emotion Analysis ViewSet
class EmotionViewSet(BaseTweetViewSet):
    """
    ViewSet for handling emotion analysis of tweets.
    """
    @action(detail=False, methods=["post"])
    def scrape(self, request):
        """
        Scrape and analyze tweets for emotion.
        """
        try:
            # Validate input
            username = request.data.get("username")
            hashtag = request.data.get("hashtag")
            max_tweets = int(request.data.get("max_tweets", 50))
            targets = [t for t in [username, hashtag] if t]
            if len(targets) != 1:
                return Response({"error": "Enter either username or hashtag, not both"}, status=400)

            # Get scraper instance
            scraper = self.get_scraper()

            # Scrape tweets
            tweets_data = scraper.scrape_tweets(
                max_tweets=max_tweets, scrape_username=username, scrape_hashtag=hashtag
            )
            if not tweets_data:
                return Response({"message": "No tweets found"}, status=200)

            # Save to database and analyze
            tweets = self.save_tweets_to_db(tweets_data)
            analyzed_tweets = []
            for tweet in tweets:
                analyzed_tweet = analyzer.analyze(tweet, "emotion")
                analyzed_tweets.append(TweetSerializer(analyzed_tweet).data)

            return Response(analyzed_tweets)
        except Exception as e:
            logger.error(f"Error in emotion analysis: {e}")
            return Response({"error": str(e)}, status=500)

def emotion_page(request):
    """
    Render the emotion analysis webpage.
    """
    return render(request, "emotion.html")

# Live Wall ViewSet
class LiveWallViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling the live wall of analyzed tweets.
    """
    queryset = Tweet.objects.all()
    serializer_class = TweetSerializer

    @action(detail=False, methods=["get"])
    def getTweets(self, request):
        """
        Fetch 100 random analyzed tweets from the database.
        """
        try:
            # Filter tweets that have been analyzed (at least one analysis field is not null)
            analyzed_tweets = Tweet.objects.filter(
                Q(sentiment__isnull=False) | Q(toxicity__isnull=False) | Q(emotion__isnull=False)
            ).order_by('?')[:100]  # Random order, limit to 100
            serialized_tweets = TweetSerializer(analyzed_tweets, many=True).data
            return Response(serialized_tweets)
        except Exception as e:
            logger.error(f"Error fetching analyzed tweets: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def livewall(request):
    """
    Render the live wall webpage.
    """
    return render(request, "livewall.html")

# Testing API View (TweetViewSet)
class TweetViewSet(viewsets.ModelViewSet):
    """
    ViewSet for testing API functionality with multiple analysis types.
    """
    queryset = Tweet.objects.all()
    serializer_class = TweetSerializer

    @classmethod
    def get_scraper(cls):
        """
        Retrieve the singleton scraper instance for this viewset.
        Reinitializes if the session is no longer connectable.
        """
        global SCAPER
        if not SCAPER.driver.service.is_connectable():
            logger.warning("Scraper session expired, reinitializing...")
            SCAPER.quit()
            SCAPER = TwitterScraper.get_instance(
                mail=os.getenv("TWITTER_MAIL"),
                username=os.getenv("TWITTER_USERNAME"),
                password=os.getenv("TWITTER_PASSWORD")
            )
        return SCAPER

    @action(detail=False, methods=["post"])
    def scrape(self, request):
        """
        Scrape and analyze tweets based on the specified analysis type.
        """
        try:
            # Validate analysis type
            analysis_type = request.data.get("analysis_type")
            if analysis_type not in ["sentiment", "toxicity", "emotion"]:
                return Response({"error": "Invalid analysis type"}, status=400)

            # Validate username or hashtag input
            username = request.data.get("username")
            hashtag = request.data.get("hashtag")
            max_tweets = int(request.data.get("max_tweets", 50))
            targets = [t for t in [username, hashtag] if t]
            if len(targets) != 1:
                return Response(
                    {"error": "Enter either username or hashtag, not both"}, status=400
                )

            # Get scraper instance
            scraper = self.get_scraper()

            # Scrape tweets
            tweets_data = scraper.scrape_tweets(
                max_tweets=max_tweets, scrape_username=username, scrape_hashtag=hashtag
            )

            if not tweets_data:
                return Response({"message": "No tweets found"}, status=200)

            # Convert scraped data to Tweet model instances
            tweets = []
            for tweet_dict in tweets_data:
                tweet, created = Tweet.objects.get_or_create(
                    tweet_id_name=f"{tweet_dict['tweet_id']}_{tweet_dict['timestamp']}",
                    defaults={
                        "handle": tweet_dict["handle"],
                        "content": tweet_dict["content"],
                        "timestamp": tweet_dict["timestamp"],
                    },
                )
                tweets.append(tweet)
            print("\n##########################################\n")
            print(tweets)

            # Analyze tweets and prepare response
            analyzed_tweets = []
            for tweet in tweets:
                analyzed_tweet = analyzer.analyze(tweet, analysis_type)
                analyzed_tweets.append(TweetSerializer(analyzed_tweet).data)

            print("\n##########################################\n")
            print(analyzed_tweets)

            return Response(analyzed_tweets)
        except Exception as e:
            logger.error(f"Error scraping tweets: {e}")
            return Response({"error": str(e)}, status=500)