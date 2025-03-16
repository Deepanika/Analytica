from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Tweet, userSearchHistory
from django.contrib.auth.models import User
from .serializers import TweetSerializer
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.urls import reverse_lazy
from .scraper import TwitterScraper
from .analyzer import analyze_tweet
from dotenv import load_dotenv
import os
import logging
from django.db.models import Q
from django.http import JsonResponse
from .forms import RegistrationForm
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Singleton scraper instance (commented out as in original)
SCAPER = TwitterScraper.get_instance(
    mail=os.getenv("TWITTER_MAIL"),
    username=os.getenv("TWITTER_USERNAME"),
    password=os.getenv("TWITTER_PASSWORD")
)
logger.info("Scraper initialized and logged in")

# Utility Functions
def get_scraper():
    """Retrieve or reinitialize the singleton Twitter scraper instance."""
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

def save_tweets_to_db(tweets_data):
    """Save scraped tweets to the database and return Tweet objects."""
    tweets = []
    for tweet_dict in tweets_data:
        tweet, _ = Tweet.objects.get_or_create(
            tweet_id_name=f"{tweet_dict['tweet_id']}_{tweet_dict['timestamp']}",
            defaults={
                "handle": tweet_dict["handle"],
                "content": tweet_dict["content"],
                "timestamp": tweet_dict["timestamp"],
            }
        )
        tweets.append(tweet)
    return tweets

# Template Views
def index(request):
    """Render the index page."""
    return render(request, "index.html")

def homepage(request):
    """Render the homepage with analysis functionality links."""
    return render(request, "homepage.html")

def sentiment_page(request):
    """Render the sentiment analysis page."""
    return render(request, "sentiment.html")

def toxicity_page(request):
    """Render the toxicity analysis page."""
    return render(request, "toxicity.html")

def emotion_page(request):
    """Render the emotion analysis page."""
    return render(request, "emotion.html")

def livewall(request):
    """Render the live wall page."""
    return render(request, "livewall.html")

class CustomLoginView(LoginView):
    template_name = 'login.html'

    def get_success_url(self):
        return reverse_lazy('homepage')
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('homepage')
        return super().dispatch(request, *args, **kwargs)

def custom_logout(request):
    logout(request)
    return redirect('login')
    
@csrf_protect
def register(request):
    if request.user.is_authenticated:
            return redirect('homepage')
    if request.method == 'POST':
        logger.info("Received POST request for user registration")
        userForm = RegistrationForm(request.POST)
        if userForm.is_valid():
            logger.info("User form is valid")
            user = userForm.save(commit=False)
            user.set_password(user.password)
            user.save()
            logger.info(f"User {user.username} registered successfully")
            return redirect('login')
        else:
            error_message = 'Username already exists. Please choose another one.'
            logger.warning(f"User form is invalid: {userForm.errors}")
            return JsonResponse({'success': False, 'message': error_message}, status=400)
    else:
        logger.info("Received GET request for user registration")
        userForm = RegistrationForm()
        return render(request, 'register.html', {'form': userForm})
# API Views
class SentimentAPIView(APIView):
    """API endpoint for scraping and analyzing tweets for sentiment."""

    def post(self, request):
        """Handle POST requests to scrape and analyze tweets for sentiment."""
        try:
            username, hashtag, max_tweets = self._validate_input(request.data)
            scraper = get_scraper()
            tweets_data = scraper.scrape_tweets(max_tweets=max_tweets, scrape_username=username, scrape_hashtag=hashtag)
            
            if not tweets_data:
                return Response({"message": "No tweets found"}, status=status.HTTP_200_OK)

            tweets = save_tweets_to_db(tweets_data)
            analyzed_tweets = [TweetSerializer(analyze_tweet(tweet, "sentiment")).data for tweet in tweets]
            return Response(analyzed_tweets)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _validate_input(self, data):
        """Validate input data for username, hashtag, and max_tweets."""
        username = data.get("username")
        hashtag = data.get("hashtag")
        max_tweets = int(data.get("max_tweets", 50))
        targets = [t for t in [username, hashtag] if t]
        if len(targets) != 1:
            raise ValueError("Enter either username or hashtag, not both")
        return username, hashtag, max_tweets

class ToxicityAPIView(APIView):
    """API endpoint for scraping and analyzing tweets for toxicity."""

    def post(self, request):
        """Handle POST requests to scrape and analyze tweets for toxicity."""
        try:
            username, hashtag, max_tweets = self._validate_input(request.data)
            scraper = get_scraper()
            tweets_data = scraper.scrape_tweets(max_tweets=max_tweets, scrape_username=username, scrape_hashtag=hashtag)
            
            if not tweets_data:
                return Response({"message": "No tweets found"}, status=status.HTTP_200_OK)

            tweets = save_tweets_to_db(tweets_data)
            analyzed_tweets = [TweetSerializer(analyze_tweet(tweet, "toxicity")).data for tweet in tweets]
            return Response(analyzed_tweets)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error in toxicity analysis: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _validate_input(self, data):
        """Validate input data for username, hashtag, and max_tweets."""
        username = data.get("username")
        hashtag = data.get("hashtag")
        max_tweets = int(data.get("max_tweets", 50))
        targets = [t for t in [username, hashtag] if t]
        if len(targets) != 1:
            raise ValueError("Enter either username or hashtag, not both")
        return username, hashtag, max_tweets

class EmotionAPIView(APIView):
    """API endpoint for scraping and analyzing tweets for emotion."""

    def post(self, request):
        """Handle POST requests to scrape and analyze tweets for emotion."""
        try:
            username, hashtag, max_tweets = self._validate_input(request.data)
            scraper = get_scraper()
            tweets_data = scraper.scrape_tweets(max_tweets=max_tweets, scrape_username=username, scrape_hashtag=hashtag)
            
            if not tweets_data:
                return Response({"message": "No tweets found"}, status=status.HTTP_200_OK)

            tweets = save_tweets_to_db(tweets_data)
            analyzed_tweets = [TweetSerializer(analyze_tweet(tweet, "emotion")).data for tweet in tweets]
            return Response(analyzed_tweets)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error in emotion analysis: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _validate_input(self, data):
        """Validate input data for username, hashtag, and max_tweets."""
        username = data.get("username")
        hashtag = data.get("hashtag")
        max_tweets = int(data.get("max_tweets", 50))
        targets = [t for t in [username, hashtag] if t]
        if len(targets) != 1:
            raise ValueError("Enter either username or hashtag, not both")
        return username, hashtag, max_tweets

class LiveWallAPIView(APIView):
    """API endpoint for fetching random analyzed tweets for the live wall."""

    def get(self, request):
        """Handle GET requests to fetch 100 random analyzed tweets."""
        try:
            analyzed_tweets = Tweet.objects.filter(
                Q(sentiment__isnull=False) | Q(toxicity__isnull=False) | Q(emotion__isnull=False)
            ).order_by('?')[:100]
            serialized_tweets = TweetSerializer(analyzed_tweets, many=True).data
            return Response(serialized_tweets)
        except Exception as e:
            logger.error(f"Error fetching analyzed tweets: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TweetAPIView(APIView):
    """API endpoint for testing tweet scraping and analysis."""

    def post(self, request):
        """Handle POST requests to scrape and analyze tweets based on analysis type."""
        try:
            analysis_type = request.data.get("analysis_type")
            if analysis_type not in ["sentiment", "toxicity", "emotion", "offensive"]:
                return Response({"error": "Invalid analysis type"}, status=status.HTTP_400_BAD_REQUEST)

            username, hashtag, max_tweets = self._validate_input(request.data)
            scraper = get_scraper()
            tweets_data = scraper.scrape_tweets(max_tweets=max_tweets, scrape_username=username, scrape_hashtag=hashtag)
            
            if not tweets_data:
                return Response({"message": "No tweets found"}, status=status.HTTP_200_OK)

            tweets = save_tweets_to_db(tweets_data)
            analyzed_tweets = [TweetSerializer(analyze_tweet(tweet, analysis_type)).data for tweet in tweets]

            # Save search history for authenticated user
            if request.user.is_authenticated:
                search_query = username if username else hashtag
                search_type = "username" if username else "hashtag"
                search_history = userSearchHistory.objects.create(
                    user=request.user,
                    search_query=search_query,
                    search_type=search_type,
                    analysis_type=analysis_type
                )
                search_history.tweets.set(tweets)
                search_history.save()
                logger.info(f"Saved search history for user {request.user.username}: {search_query}")

            return Response(analyzed_tweets)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error scraping tweets: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _validate_input(self, data):
        """Validate input data for username, hashtag, and max_tweets."""
        username = data.get("username")
        hashtag = data.get("hashtag")
        max_tweets = int(data.get("max_tweets", 50))
        targets = [t for t in [username, hashtag] if t]
        if len(targets) != 1:
            raise ValueError("Enter either username or hashtag, not both")
        return username, hashtag, max_tweets

@login_required
def history_page(request):
    """Render the history page with user's search history."""
    search_history = userSearchHistory.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'history.html', {'search_history': search_history})

class HistoryAPIView(APIView):
    """API endpoint to fetch tweets from a user's search history."""

    def get(self, request, history_id):
        """Handle GET requests to fetch tweets for a specific search history entry."""
        try:
            if not request.user.is_authenticated:
                return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
            
            history = userSearchHistory.objects.get(id=history_id, user=request.user)
            tweets = history.tweets.all()
            serialized_tweets = TweetSerializer(tweets, many=True).data
            return Response({"tweets": serialized_tweets})
        except userSearchHistory.DoesNotExist:
            return Response({"error": "Search history not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error fetching history tweets: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)