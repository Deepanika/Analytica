from django.contrib import admin
from .models import User, Tweet, userSearchHistory

admin.site.register(User)
admin.site.register(Tweet)
admin.site.register(userSearchHistory)
