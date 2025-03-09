from django.db import models

# Create your models here.
class Admin(models.Model):
    admin_id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=10)
    email = models.EmailField()
    password = models.CharField(max_length=255)
    is_autheticated = models.BooleanField(default=False)
    
    def __str__(self):
        return self.username
    
class Tweet(models.Model):
    id = models.AutoField(primary_key=True)  # Explicit primary key
    tweet_id_name = models.CharField(max_length=255)  # Twitter user ID (not unique)
    content = models.TextField()
    handle = models.CharField(max_length=255)
    timestamp = models.CharField(max_length=255)
    sentiment = models.CharField(max_length=20, blank=True, default="NA")
    toxicity = models.CharField(max_length=20, blank=True, default="NA")
    emotion = models.CharField(max_length=20, blank=True, default="NA")

    def __str__(self):
        return self.content[:50]
