from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('twitter_app.urls')),  # Include the URLs from twitter_app
]