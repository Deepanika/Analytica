from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import index, TweetViewSet

router = DefaultRouter()
router.register(r'tweets', TweetViewSet)

urlpatterns = [
    path('home/', index, name='index'),
    path('api/', include(router.urls)),

]
