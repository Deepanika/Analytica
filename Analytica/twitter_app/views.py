from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Tweet, userSearchHistory, User
from .serializers import TweetSerializer
from .scraper import TwitterScraper
from .analyzer import analyze_tweet
from dotenv import load_dotenv
import os
import logging
from django.db.models import Q
from .forms import RegistrationForm
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
# load_dotenv()

# # # Singleton scraper instance
# SCAPER = TwitterScraper.get_instance(
#     mail=os.getenv("TWITTER_MAIL"),
#     username=os.getenv("TWITTER_USERNAME"),
#     password=os.getenv("TWITTER_PASSWORD")
# )
# logger.info("Scraper initialized and logged in")

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


class LogoutAPIView(APIView):
    """API endpoint for user logout."""
    def post(self, request):
        logout(request)  # Clears session
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)

class AuthStatusAPIView(APIView):
    """API endpoint to check if user is authenticated."""
    def get(self, request):
        if request.user.is_authenticated:
            return Response({'is_authenticated': True, 'username': request.user.username})
        return Response({'is_authenticated': False})

# ✅ LOGIN VIEW WITH RESTRICTION
class LoginAPIView(APIView):
    """API endpoint for user login using session-based authentication."""
    def post(self, request):
        if request.user.is_authenticated:
            return Response({'detail': 'Already logged in'}, status=status.HTTP_400_BAD_REQUEST)
        
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)  # Sets session cookie
            return Response({
                'message': 'Logged in successfully',
                'user_id': user.user_id,
                'username': user.username
            }, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

# ✅ REGISTER VIEW WITH RESTRICTION
class RegisterAPIView(APIView):
    """API endpoint for user registration."""
    def post(self, request):
        if request.user.is_authenticated:
            return Response({'detail': 'Already logged in'}, status=status.HTTP_400_BAD_REQUEST)

        form = RegistrationForm(request.data)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response({'errors': form.errors}, status=status.HTTP_400_BAD_REQUEST)

def set_csrf_token(request):
    return JsonResponse({"message": "CSRF cookie set."})

class IndexAPIView(APIView):
    """API endpoint replacing the index page."""
    def get(self, request):
        return Response({'message': 'Welcome to the index page'})

class HomepageAPIView(APIView):
    """API endpoint replacing the homepage."""
    def get(self, request):
        return Response({'message': 'Welcome to the homepage'})

class SentimentAPIView(APIView):
    """API endpoint for scraping and analyzing tweets for sentiment."""
    def post(self, request):
        try:
            username, hashtag, max_tweets = self._validate_input(request.data)
            scraper = get_scraper()
            tweets_data = scraper.scrape_tweets(
                max_tweets=max_tweets,
                scrape_username=username,
                scrape_hashtag=hashtag
            )
            
            if not tweets_data:
                return Response({"message": "No tweets found"}, status=status.HTTP_200_OK)

            tweets = save_tweets_to_db(tweets_data)
            analyzed_tweets = []

            for tweet in tweets:
                tweet_data = TweetSerializer(tweet).data  # ✅ Serialize tweet fields
                tweet_data['sentiment'] = analyze_tweet(tweet, "sentiment")  # ✅ Add sentiment result
                analyzed_tweets.append(tweet_data)  # ✅ Append combined data

            if request.user.is_authenticated:
                search_query = username if username else hashtag
                search_type = "username" if username else "hashtag"
                search_history = userSearchHistory.objects.create(
                    user=request.user,
                    search_query=search_query,
                    search_type=search_type,
                    analysis_type="senitment"
                )
                search_history.tweets.set(tweets)
                search_history.save()
            return Response(analyzed_tweets, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def _validate_input(self, data):
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
        try:
            username, hashtag, max_tweets = self._validate_input(request.data)
            scraper = get_scraper()
            tweets_data = scraper.scrape_tweets(
                max_tweets=max_tweets,
                scrape_username=username,
                scrape_hashtag=hashtag
            )
            
            if not tweets_data:
                return Response({"message": "No tweets found"}, status=status.HTTP_200_OK)

            tweets = save_tweets_to_db(tweets_data)
            analyzed_tweets = []

            for tweet in tweets:
                tweet_data = TweetSerializer(tweet).data  # ✅ Serialize tweet fields
                tweet_data['toxicity'] = analyze_tweet(tweet, "toxicity")  # ✅ Add toxicity result
                analyzed_tweets.append(tweet_data)  # ✅ Append combined data

            if request.user.is_authenticated:
                search_query = username if username else hashtag
                search_type = "username" if username else "hashtag"
                search_history = userSearchHistory.objects.create(
                    user=request.user,
                    search_query=search_query,
                    search_type=search_type,
                    analysis_type="toxicity"
                )
                search_history.tweets.set(tweets)
                search_history.save()
            return Response(analyzed_tweets, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error in toxicity analysis: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def _validate_input(self, data):
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
        try:
            username, hashtag, max_tweets = self._validate_input(request.data)
            scraper = get_scraper()
            tweets_data = scraper.scrape_tweets(
                max_tweets=max_tweets,
                scrape_username=username,
                scrape_hashtag=hashtag
            )
            
            if not tweets_data:
                return Response({"message": "No tweets found"}, status=status.HTTP_200_OK)

            tweets = save_tweets_to_db(tweets_data)
            analyzed_tweets = []

            for tweet in tweets:
                tweet_data = TweetSerializer(tweet).data  # ✅ Serialize tweet fields
                tweet_data['emotion'] = analyze_tweet(tweet, "emotion")  # ✅ Add analysis result
                analyzed_tweets.append(tweet_data)
            
            if request.user.is_authenticated:
                search_query = username if username else hashtag
                search_type = "username" if username else "hashtag"
                search_history = userSearchHistory.objects.create(
                    user=request.user,
                    search_query=search_query,
                    search_type=search_type,
                    analysis_type="emotion"
                )
                search_history.tweets.set(tweets)
                search_history.save()

            return Response(analyzed_tweets, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error in emotion analysis: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def _validate_input(self, data):
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
    """API endpoint for combined and specific analysis on tweets."""

    def post(self, request):
        try:
            analysis_type = request.data.get("analysis_type")
            if analysis_type not in ["sentiment", "toxicity", "emotion", "offensive", "combined"]:
                return Response({"error": "Invalid analysis type"}, status=status.HTTP_400_BAD_REQUEST)

            username, hashtag, max_tweets = self._validate_input(request.data)
            scraper = get_scraper()
            tweets_data = scraper.scrape_tweets(
                max_tweets=max_tweets, scrape_username=username, scrape_hashtag=hashtag
            )

            if not tweets_data:
                return Response({"message": "No tweets found"}, status=status.HTTP_200_OK)

            tweets = save_tweets_to_db(tweets_data)
            analyzed_tweets = []

            for tweet in tweets:
                tweet_data = TweetSerializer(tweet).data  # ✅ Serialize tweet fields

                # ✅ Add analysis results
                if analysis_type == "combined":
                    tweet_data["sentiment"] = analyze_tweet(tweet, "sentiment")  # string result
                    tweet_data["toxicity"] = analyze_tweet(tweet, "toxicity")
                    tweet_data["emotion"] = analyze_tweet(tweet, "emotion")
                else:
                    tweet_data[analysis_type] = analyze_tweet(tweet, analysis_type)  # single analysis

                analyzed_tweets.append(tweet_data)  # ✅ Now contains all tweet data + analysis

            # ✅ Save search history
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

            return Response(analyzed_tweets, status=200)  # ✅ Ready for frontend

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error scraping tweets: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _validate_input(self, data):
        username = data.get("username")
        hashtag = data.get("hashtag")
        max_tweets = int(data.get("max_tweets", 50))
        targets = [t for t in [username, hashtag] if t]
        if len(targets) != 1:
            raise ValueError("Enter either username or hashtag, not both")
        return username, hashtag, max_tweets


class HistoryAPIView(APIView):
    """API endpoint to fetch tweets from a user's search history."""
    permission_classes = [IsAuthenticated]  # Restrict to logged-in users
    def get(self, request, history_id):
        try:
            history = userSearchHistory.objects.get(id=history_id, user=request.user)
            tweets = history.tweets.all()
            serialized_tweets = TweetSerializer(tweets, many=True).data
            return Response({"tweets": serialized_tweets})
        except userSearchHistory.DoesNotExist:
            return Response({"error": "Search history not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error fetching history tweets: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class HistoryPageAPIView(APIView):
    """API endpoint replacing the history page."""
    permission_classes = [IsAuthenticated]
    def get(self, request):
        search_history = userSearchHistory.objects.filter(user=request.user).order_by('-timestamp')
        serialized_history = [
            {
                'id': entry.id,
                'search_query': entry.search_query,
                'search_type': entry.search_type,
                'analysis_type': entry.analysis_type,
                'timestamp': entry.timestamp
            } for entry in search_history
        ]
        return Response({'search_history': serialized_history})