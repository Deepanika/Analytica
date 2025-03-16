from django.urls import path
from . import views

urlpatterns = [
    path('test/', views.index, name='index'),
    path('home/', views.homepage, name='homepage'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('livewall/', views.livewall, name='livewall'),
    path('sentiment/', views.sentiment_page, name='sentiment'),
    path('toxicity/', views.toxicity_page, name='toxicity'),
    path('emotion/', views.emotion_page, name='emotion'),
    path('history/', views.history_page, name='history'),
    # API views
    path('api/tweet/scrape/', views.TweetAPIView.as_view(), name='tweet_scrape'),
    path('api/sentiment/scrape/', views.SentimentAPIView.as_view(), name='sentiment_scrape'),
    path('api/toxicity/scrape/', views.ToxicityAPIView.as_view(), name='toxicity_scrape'),
    path('api/emotion/scrape/', views.EmotionAPIView.as_view(), name='emotion_scrape'),
    path('api/livewall/getTweets/', views.LiveWallAPIView.as_view(), name='livewall_get_tweets'),
    path('api/history/tweets/<int:history_id>/', views.HistoryAPIView.as_view(), name='history_tweets'),
]