from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import index, TweetViewSet, homepage, livewall,SentimentViewSet,ToxicityViewSet,EmotionViewSet,LiveWallViewSet

router = DefaultRouter()
router.register(r'tweets', TweetViewSet)
router.register(r'sentiment', SentimentViewSet, basename='sentiment')
router.register(r'toxicity', ToxicityViewSet, basename='toxicity')
router.register(r'emotion', EmotionViewSet, basename='emotion')
router.register(r'livewall',LiveWallViewSet, basename='livewall')

urlpatterns = [
    path('test/', index, name='index'),
    path('api/', include(router.urls)),
    path('home/', homepage,name='homepage'),
    path('livewall/', livewall,name='livewall')
    # path('sentiment/', views.sentiment_page, name='sentiment'),
    # path('toxicity/', views.toxicity_page, name='toxicity'),
    # path('emotion/', views.emotion_page, name='emotion'),

]
