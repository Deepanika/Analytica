import joblib
import pickle
from .models import Tweet  # Import the Tweet model
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import numpy as np
from scipy.special import softmax

def preprocess(text):
    new_text = []
    for t in text.split(" "):
        t = '@user' if t.startswith('@') and len(t) > 1 else t
        t = 'http' if t.startswith('http') else t
        new_text.append(t)
    return " ".join(new_text)

class BaseAnalyzer:
    def analyze(self, tweet):
        raise NotImplementedError("Subclasses must implement this method")

class SingletonMeta(type):
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class SentimentAnalyzer(BaseAnalyzer, metaclass=SingletonMeta):
    def __init__(self):
        if not hasattr(self, '_initialized'):
            try:
                self.model = AutoModelForSequenceClassification.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment")
                self.tokenizer = AutoTokenizer.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment")
                self.labels = ["Negative", "Neutral", "Positive"]
                self._initialized = True
            except Exception as e:
                print(f"Error loading sentiment model or tokenizer: {e}")
                self.model = None
                self.tokenizer = None
                self._initialized = False

    def analyze(self, tweet):
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Sentiment model or tokenizer not initialized.")
        content = preprocess(tweet.content)
        encoded_input = self.tokenizer(content, return_tensors='pt')
        output = self.model(**encoded_input)
        scores = output[0][0].detach().numpy()
        scores = softmax(scores)
        sentiment = self.labels[np.argmax(scores)]
        tweet.sentiment = sentiment
        tweet.save()
        return sentiment

class ToxicityAnalyzer(BaseAnalyzer, metaclass=SingletonMeta):
    def __init__(self):
        if not hasattr(self, '_initialized'):
            try:
                self.model = AutoModelForSequenceClassification.from_pretrained("cardiffnlp/twitter-roberta-base-offensive")
                self.tokenizer = AutoTokenizer.from_pretrained("cardiffnlp/twitter-roberta-base-offensive")
                self.labels = ["not-offensive", "offensive"]
                self._initialized = True
            except Exception as e:
                print(f"Error loading offensive model or tokenizer: {e}")
                self.model = None
                self.tokenizer = None
                self._initialized = False

    def analyze(self, tweet):
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Toxicity model or tokenizer not initialized.")
        content = preprocess(tweet.content)
        encoded_input = self.tokenizer(content, return_tensors='pt')
        output = self.model(**encoded_input)
        scores = output[0][0].detach().numpy()
        scores = softmax(scores)
        toxicity = self.labels[np.argmax(scores)]
        tweet.toxicity = toxicity
        tweet.save()
        return toxicity

class EmotionAnalyzer(BaseAnalyzer, metaclass=SingletonMeta):
    def __init__(self):
        if not hasattr(self, '_initialized'):
            try:
                self.model = AutoModelForSequenceClassification.from_pretrained("cardiffnlp/twitter-roberta-base-emotion")
                self.tokenizer = AutoTokenizer.from_pretrained("cardiffnlp/twitter-roberta-base-emotion")
                self.labels = ["anger", "joy", "optimism", "sadness"]
                self._initialized = True
            except Exception as e:
                print(f"Error loading emotion model or tokenizer: {e}")
                self.model = None
                self.tokenizer = None
                self._initialized = False

    def analyze(self, tweet):
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Emotion model or tokenizer not initialized.")
        content = preprocess(tweet.content)
        encoded_input = self.tokenizer(content, return_tensors='pt')
        output = self.model(**encoded_input)
        scores = output[0][0].detach().numpy()
        scores = softmax(scores)
        emotion = self.labels[np.argmax(scores)]
        tweet.emotion = emotion
        tweet.save()
        return emotion

class AnalyzerFactory:
    _analyzers = {
        'sentiment': SentimentAnalyzer(),
        'toxicity': ToxicityAnalyzer(),
        'emotion': EmotionAnalyzer()
    }

    @staticmethod
    def get_analyzer(analysis_type):
        if analysis_type not in AnalyzerFactory._analyzers:
            raise ValueError(f"Unknown analysis type: {analysis_type}")
        return AnalyzerFactory._analyzers[analysis_type]

# Example usage
def analyze_tweet(tweet, analysis_type):
    analyzer = AnalyzerFactory.get_analyzer(analysis_type)
    return analyzer.analyze(tweet)