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

logger = logging.getLogger(__name__)


def index(request):
    return render(request, "index.html")


class TweetViewSet(viewsets.ModelViewSet):
    queryset = Tweet.objects.all()
    serializer_class = TweetSerializer

    # Initialize the scraper once and reuse it
    load_dotenv()
    USER_MAIL = os.getenv("TWITTER_MAIL")
    USER_UNAME = os.getenv("TWITTER_USERNAME")
    USER_PASSWORD = os.getenv("TWITTER_PASSWORD")
    scraper = TwitterScraper(
        mail=USER_MAIL, username=USER_UNAME, password=USER_PASSWORD
    )

    @action(detail=False, methods=["post"])
    def scrape(self, request):
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

            # Scrape tweets
            tweets_data = self.scraper.scrape_tweets(
                max_tweets=max_tweets, scrape_username=username, scrape_hashtag=hashtag
            )

            if not tweets_data:
                return Response({"message": "No tweets found"}, status=200)

            # Convert scraped data to Tweet model instances
            tweets = []
            for tweet_dict in tweets_data:
                tweet, created = Tweet.objects.get_or_create(
                    tweet_id_name=f"{tweet_dict['tweet_id']}_{tweet_dict['timestamp']}",  # ✅ Ensure uniqueness
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
