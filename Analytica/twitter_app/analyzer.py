import joblib
import pickle
from .models import Tweet  # Import the Tweet model

class Analyzer:
    def __init__(self):
        # Load the sentiment model and vectorizer using joblib
        try:
            self.sentiment_model = joblib.load('models/sentiment_model.pkl')
            self.sentiment_vectorizer = joblib.load('models/tfidf_vectorizer.pkl')
        except (FileNotFoundError, joblib.externals.loky.process_executor._RemoteTraceback) as e:
            print(f"Error loading sentiment model or vectorizer: {e}")
            self.sentiment_model = None
            self.sentiment_vectorizer = None

        # Load the toxicity model using pickle
        try:
            with open('models/toxicity_model.pkl', 'rb') as file:
                self.toxicity_model = pickle.load(file)
        except (FileNotFoundError, pickle.UnpicklingError) as e:
            print(f"Error loading toxicity model: {e}")
            self.toxicity_model = None

        self.emotion_model = None  # Placeholder

    def analyze(self, tweet, analysis_type):
        content = tweet.content
        if not content.strip():
            if analysis_type == 'sentiment':
                tweet.sentiment = "Unknown"
            elif analysis_type == 'toxicity':
                tweet.toxicity = "Unknown"
            elif analysis_type == 'emotion':
                tweet.emotion = "Unknown"
            tweet.save()
            return tweet

        if analysis_type == 'sentiment' and self.sentiment_model and self.sentiment_vectorizer:
            # Transform the content using the vectorizer and predict sentiment
            content_vectorized = self.sentiment_vectorizer.transform([content])
            sentiment = self.sentiment_model.predict(content_vectorized)[0]
            tweet.sentiment = "Positive" if sentiment == 1 else "Negative"
        elif analysis_type == 'toxicity' and self.toxicity_model:
            # Predict toxicity directly without vectorizing the content
            toxicity = self.toxicity_model.predict([content])[0]
            tweet.toxicity = "Toxic" if toxicity == 1 else "Non-Toxic"
        elif analysis_type == 'emotion':
            # Placeholder until emotion model is implemented
            tweet.emotion = "Happy"  # Mock emotion

        tweet.save()
        return tweet

analyzer = Analyzer()