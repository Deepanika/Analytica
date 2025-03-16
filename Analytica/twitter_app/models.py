from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=10, unique=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username
class Tweet(models.Model):
    id = models.AutoField(primary_key=True)
    tweet_id_name = models.CharField(max_length=255)
    content = models.TextField()
    handle = models.CharField(max_length=255)
    timestamp = models.CharField(max_length=255)
    sentiment = models.CharField(max_length=20, blank=True, default="NA")
    toxicity = models.CharField(max_length=20, blank=True, default="NA")
    emotion = models.CharField(max_length=20, blank=True, default="NA")

    def __str__(self):
        return self.content[:50]


class userSearchHistory(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    search_query = models.CharField(max_length=255)
    search_type  = models.CharField(max_length=255)
    analysis_type  = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    tweets = models.ManyToManyField(Tweet)

    def __str__(self):
        return f"{self.user.username} searched for {self.search_query} on {self.timestamp}"