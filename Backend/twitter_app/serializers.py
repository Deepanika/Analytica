from rest_framework import serializers
from .models import Tweet

# class AnalysisResultSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = AnalysisResult
#         fields = ['sentiment_score', 'toxicity_score', 'emotion_score']

class TweetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tweet
        fields = ['handle', 'content', 'sentiment', 'toxicity', 'emotion','timestamp']