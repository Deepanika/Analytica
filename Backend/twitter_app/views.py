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
from langdetect import detect
from deep_translator import GoogleTranslator
from django.db.models import Count, Avg

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Singleton scraper instance
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

def detect_language(text):
    """Detect the language of the given text."""
    try:
        return detect(text)
    except Exception as e:
        logger.error(f"Language detection error: {e}")
        return 'unknown'

def translate_to_english(text):
    """Translate text to English using GoogleTranslator."""
    try:
        translator = GoogleTranslator(source='auto', target='en')
        return translator.translate(text)
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return text  # Fallback to original text if translation fails

# Authentication and Utility Views
class LogoutAPIView(APIView):
    def post(self, request):
        logout(request)
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)

class AuthStatusAPIView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            return Response({'is_authenticated': True, 'username': request.user.username})
        return Response({'is_authenticated': False})

class LoginAPIView(APIView):
    def post(self, request):
        if request.user.is_authenticated:
            return Response({'detail': 'Already logged in'}, status=status.HTTP_400_BAD_REQUEST)
        
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({
                'message': 'Logged in successfully',
                'user_id': user.user_id,
                'username': user.username
            }, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class RegisterAPIView(APIView):
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

@ensure_csrf_cookie
def set_csrf_token(request):
    return JsonResponse({"message": "CSRF cookie set."})

class IndexAPIView(APIView):
    def get(self, request):
        return Response({'message': 'Welcome to the index page'})

class HomepageAPIView(APIView):
    def get(self, request):
        return Response({'message': 'Welcome to the homepage'})

# Tweet Analysis Views
class SentimentAPIView(APIView):
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

            analyzed_tweets = []
            tweets_objects = []

            for tweet_dict in tweets_data:
                original_content = tweet_dict['content']
                language = detect_language(original_content)
                if language != 'en':
                    translated_content = translate_to_english(original_content)
                    content_for_analysis = translated_content
                else:
                    translated_content = None
                    content_for_analysis = original_content
                
                sentiment = analyze_tweet(content_for_analysis, "sentiment")
                
                tweet, created = Tweet.objects.update_or_create(
                    tweet_id_name=f"{tweet_dict['tweet_id']}_{tweet_dict['timestamp']}",
                    defaults={
                        "handle": tweet_dict["handle"],
                        "content": original_content,
                        "translated_content": translated_content,
                        "timestamp": tweet_dict["timestamp"],
                        "sentiment": sentiment,
                    }
                )
                tweets_objects.append(tweet)
                
                tweet_data = TweetSerializer(tweet).data
                analyzed_tweets.append(tweet_data)

            if request.user.is_authenticated:
                search_query = username if username else hashtag
                search_type = "username" if username else "hashtag"
                search_history = userSearchHistory.objects.create(
                    user=request.user,
                    search_query=search_query,
                    search_type=search_type,
                    analysis_type="sentiment"
                )
                search_history.tweets.set(tweets_objects)
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
        max_tweets = int(data.get("max_tweets", 100))
        targets = [t for t in [username, hashtag] if t]
        if len(targets) != 1:
            raise ValueError("Enter either username or hashtag, not both")
        return username, hashtag, max_tweets

class ToxicityAPIView(APIView):
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

            analyzed_tweets = []
            tweets_objects = []

            for tweet_dict in tweets_data:
                original_content = tweet_dict['content']
                language = detect_language(original_content)
                if language != 'en':
                    translated_content = translate_to_english(original_content)
                    content_for_analysis = translated_content
                else:
                    translated_content = None
                    content_for_analysis = original_content
                
                toxicity = analyze_tweet(content_for_analysis, "toxicity")
                
                tweet, created = Tweet.objects.update_or_create(
                    tweet_id_name=f"{tweet_dict['tweet_id']}_{tweet_dict['timestamp']}",
                    defaults={
                        "handle": tweet_dict["handle"],
                        "content": original_content,
                        "translated_content": translated_content,
                        "timestamp": tweet_dict["timestamp"],
                        "toxicity": toxicity,
                    }
                )
                tweets_objects.append(tweet)
                
                tweet_data = TweetSerializer(tweet).data
                analyzed_tweets.append(tweet_data)

            if request.user.is_authenticated:
                search_query = username if username else hashtag
                search_type = "username" if username else "hashtag"
                search_history = userSearchHistory.objects.create(
                    user=request.user,
                    search_query=search_query,
                    search_type=search_type,
                    analysis_type="toxicity"
                )
                search_history.tweets.set(tweets_objects)
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

            analyzed_tweets = []
            tweets_objects = []

            for tweet_dict in tweets_data:
                original_content = tweet_dict['content']
                language = detect_language(original_content)
                if language != 'en':
                    translated_content = translate_to_english(original_content)
                    content_for_analysis = translated_content
                else:
                    translated_content = None
                    content_for_analysis = original_content
                
                emotion = analyze_tweet(content_for_analysis, "emotion")
                
                tweet, created = Tweet.objects.update_or_create(
                    tweet_id_name=f"{tweet_dict['tweet_id']}_{tweet_dict['timestamp']}",
                    defaults={
                        "handle": tweet_dict["handle"],
                        "content": original_content,
                        "translated_content": translated_content,
                        "timestamp": tweet_dict["timestamp"],
                        "emotion": emotion,
                    }
                )
                tweets_objects.append(tweet)
                
                tweet_data = TweetSerializer(tweet).data
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
                search_history.tweets.set(tweets_objects)
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

class TweetAPIView(APIView):
    def post(self, request):
        try:
            analysis_type = request.data.get("analysis_type")
            if analysis_type not in ["sentiment", "toxicity", "emotion", "combined"]:
                return Response({"error": "Invalid analysis type"}, status=status.HTTP_400_BAD_REQUEST)

            username, hashtag, max_tweets = self._validate_input(request.data)
            scraper = get_scraper()
            tweets_data = scraper.scrape_tweets(
                max_tweets=max_tweets,
                scrape_username=username,
                scrape_hashtag=hashtag
            )

            if not tweets_data:
                return Response({"message": "No tweets found"}, status=status.HTTP_200_OK)

            analyzed_tweets = []
            tweets_objects = []

            for tweet_dict in tweets_data:
                original_content = tweet_dict['content']
                language = detect_language(original_content)
                if language != 'en':
                    translated_content = translate_to_english(original_content)
                    content_for_analysis = translated_content
                else:
                    translated_content = None
                    content_for_analysis = original_content

                if analysis_type == "combined":
                    sentiment = analyze_tweet(content_for_analysis, "sentiment")
                    toxicity = analyze_tweet(content_for_analysis, "toxicity")
                    emotion = analyze_tweet(content_for_analysis, "emotion")
                    defaults = {
                        "handle": tweet_dict["handle"],
                        "content": original_content,
                        "translated_content": translated_content,
                        "timestamp": tweet_dict["timestamp"],
                        "sentiment": sentiment,
                        "toxicity": toxicity,
                        "emotion": emotion,
                    }
                else:
                    result = analyze_tweet(content_for_analysis, analysis_type)
                    defaults = {
                        "handle": tweet_dict["handle"],
                        "content": original_content,
                        "translated_content": translated_content,
                        "timestamp": tweet_dict["timestamp"],
                        analysis_type: result,
                    }

                tweet, created = Tweet.objects.update_or_create(
                    tweet_id_name=f"{tweet_dict['tweet_id']}_{tweet_dict['timestamp']}",
                    defaults=defaults
                )
                tweets_objects.append(tweet)
                
                tweet_data = TweetSerializer(tweet).data
                analyzed_tweets.append(tweet_data)

            if request.user.is_authenticated:
                search_query = username if username else hashtag
                search_type = "username" if username else "hashtag"
                search_history = userSearchHistory.objects.create(
                    user=request.user,
                    search_query=search_query,
                    search_type=search_type,
                    analysis_type=analysis_type
                )
                search_history.tweets.set(tweets_objects)
                search_history.save()

            return Response(analyzed_tweets, status=status.HTTP_200_OK)

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

# Display Views
class LiveWallAPIView(APIView):
    def get(self, request):
        try:
            # Fetch tweets with sentiment, toxicity, or emotion analysis
            analyzed_tweets = Tweet.objects.filter(
                Q(sentiment__isnull=False) | Q(toxicity__isnull=False) | Q(emotion__isnull=False)
            ).order_by('-timestamp')[:50]  # Fetch the latest 50 tweets
            serialized_tweets = TweetSerializer(analyzed_tweets, many=True).data
            return Response(serialized_tweets, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching live tweets: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class HistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]
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

class LeaderboardAPIView(APIView):
    def get(self, request):
        try:
            # Get query parameters
            board_type = request.query_params.get('type', 'username')  # 'username' or 'hashtag'
            category = request.query_params.get('category', 'positive')  # 'positive', 'negative', 'toxic', etc.
            limit = int(request.query_params.get('limit', 10))  # Number of results to return
            
            # Initialize query based on board type
            if board_type == 'username':
                queryset = Tweet.objects.values('handle')
            elif board_type == 'hashtag':
                return Response(self._get_hashtag_leaderboard(category, limit))
            else:
                return Response({"error": "Invalid type. Use 'username' or 'hashtag'."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Apply filters based on category
            if category == 'positive':
                queryset = queryset.filter(sentiment='Positive').annotate(count=Count('id')).order_by('-count')
            elif category == 'negative':
                queryset = queryset.filter(sentiment='Negative').annotate(count=Count('id')).order_by('-count')
            elif category == 'toxic':
                queryset = queryset.filter(toxicity='offensive').annotate(count=Count('id')).order_by('-count')
            elif category == 'non_toxic':
                queryset = queryset.filter(toxicity='not-offensive').annotate(count=Count('id')).order_by('-count')
            elif category in ['joy', 'sadness', 'anger', 'optimism']:
                queryset = queryset.filter(emotion=category).annotate(count=Count('id')).order_by('-count')
            elif category == 'active':
                queryset = queryset.annotate(count=Count('id')).order_by('-count')
            else:
                return Response({"error": "Invalid category."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Limit the results
            results = queryset[:limit]
            
            # Get a sample tweet for each entry
            leaderboard = []
            for entry in results:
                item = {
                    board_type: entry['handle'] if board_type == 'username' else entry['hashtag'],
                    'count': entry['count'],
                    'rank': list(results).index(entry) + 1
                }
                sample_tweet = Tweet.objects.filter(handle=entry['handle']).order_by('-timestamp').first() if board_type == 'username' else None
                if sample_tweet:
                    item['sample_tweet'] = TweetSerializer(sample_tweet).data
                leaderboard.append(item)
            
            return Response({
                'leaderboard_type': board_type,
                'category': category,
                'results': leaderboard
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error generating leaderboard: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_hashtag_leaderboard(self, category, limit):
        """Generate hashtag leaderboard by analyzing tweet content for hashtags"""
        import re
        from collections import Counter
        
        hashtag_count = Counter()
        
        # Get tweets based on category
        if category == 'positive':
            tweets = Tweet.objects.filter(sentiment='Positive')
        elif category == 'negative':
            tweets = Tweet.objects.filter(sentiment='Negative')
        elif category == 'toxic':
            tweets = Tweet.objects.filter(toxicity='offensive')
        elif category == 'non_toxic':
            tweets = Tweet.objects.filter(toxicity='not-offensive')
        elif category in ['joy', 'sadness', 'anger', 'optimism']:
            tweets = Tweet.objects.filter(emotion=category)
        else:  # active
            tweets = Tweet.objects.all()
        
        # Extract hashtags from tweets
        for tweet in tweets:
            hashtags = re.findall(r'#(\w+)', tweet.content)
            for tag in hashtags:
                hashtag_count[tag.lower()] += 1
        
        # Convert to required format
        results = []
        rank = 1
        for tag, count in hashtag_count.most_common(limit):
            sample_tweet = Tweet.objects.filter(content__icontains=f'#{tag}').order_by('-timestamp').first()
            item = {
                'hashtag': tag,
                'count': count,
                'rank': rank
            }
            if sample_tweet:
                item['sample_tweet'] = TweetSerializer(sample_tweet).data
            
            results.append(item)
            rank += 1
        
        return {
            'leaderboard_type': 'hashtag',
            'category': category,
            'results': results
        }