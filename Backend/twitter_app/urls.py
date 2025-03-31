from django.urls import path
from . import views

urlpatterns = [
    # Authentication API endpoints
    path('api/auth/login/', views.LoginAPIView.as_view(), name='login'),
    path('api/auth/logout/', views.LogoutAPIView.as_view(), name='logout'),
    path('api/auth/register/', views.RegisterAPIView.as_view(), name='register'),
    path('api/auth/status/', views.AuthStatusAPIView.as_view(), name='auth_status'), 
    path('api/auth/csrf/', views.set_csrf_token, name='set_csrf'),
    
    # Page replacement API endpoints
    path('api/index/', views.IndexAPIView.as_view(), name='index'),
    path('api/home/', views.HomepageAPIView.as_view(), name='homepage'),
    path('api/history/', views.HistoryPageAPIView.as_view(), name='history'),
    
    # Existing API endpoints
    path('api/combined/scrape/', views.TweetAPIView.as_view(), name='tweet_scrape'),
    path('api/sentiment/scrape/', views.SentimentAPIView.as_view(), name='sentiment_scrape'),
    path('api/toxicity/scrape/', views.ToxicityAPIView.as_view(), name='toxicity_scrape'),
    path('api/emotion/scrape/', views.EmotionAPIView.as_view(), name='emotion_scrape'),
    path('api/livewall/', views.LiveWallAPIView.as_view(), name='livewall_get_tweets'),
    path('api/history/tweets/<int:history_id>/', views.HistoryAPIView.as_view(), name='history_tweets'),
    path('api/leaderboard/', views.LeaderboardAPIView.as_view(), name='leaderboard'),
]