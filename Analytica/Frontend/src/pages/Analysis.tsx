import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { AnalysisForm } from '../components/AnalysisForm';
import { BackgroundTweets } from '../components/BackgroundTweets';
import { TweetCard } from '../components/TweetCard';
import { ArrowLeft } from 'lucide-react';
import { getCookie } from '../utils/csrf';

const backgrounds = {
  combined: 'from-gray-900 to-black',
  emotional: 'from-gray-900 to-black',
  toxicity: 'from-gray-900 to-black',
  sentimental: 'from-gray-900 to-black',
};

export const Analysis = () => {
  const { type = 'combined' } = useParams<{ type: 'combined' | 'emotional' | 'toxicity' | 'sentimental' }>();
  const [result, setResult] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const apiPaths: Record<string, string> = {
    combined: 'http://localhost:8000/api/combined/scrape/',
    emotional: 'http://localhost:8000/api/emotion/scrape/',
    toxicity: 'http://localhost:8000/api/toxicity/scrape/',
    sentimental: 'http://localhost:8000/api/sentiment/scrape/',
  };

  const mapTypeToAnalysis = (type: string) => {
    if (type === 'sentimental') return 'sentiment';
    return type;
  };

  const handleAnalysis = async (data: { query: string; tweetCount: number }) => {
    setLoading(true);
    setError(null);
    setResult([]);
    console.log('Analyzing:', { type, ...data });

    const username = data.query.startsWith('@') ? data.query.slice(1) : null;
    const hashtag = data.query.startsWith('#') ? data.query.slice(1) : null;

    if (!username && !hashtag) {
      setError('Please enter a valid @username or #hashtag.');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(apiPaths[type], {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken') || '',
        },
        credentials: 'include',
        body: JSON.stringify({
          analysis_type: mapTypeToAnalysis(type),
          username: username,
          hashtag: hashtag,
          max_tweets: data.tweetCount,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Analysis failed:', errorText);
        setError('Analysis failed: ' + response.status);
      } else {
        const jsonData = await response.json();
        console.log('Analysis result:', jsonData);
        setResult(jsonData);
      }
    } catch (err) {
      console.error('Error:', err);
      setError('An unexpected error occurred.');
    }

    setLoading(false);
  };

  return (
    <div className={`min-h-screen bg-gradient-to-br ${backgrounds[type]} text-white relative overflow-hidden`}>
      <BackgroundTweets />

      <Link
        to="/"
        className="absolute top-6 left-6 flex items-center gap-2 text-white/60 hover:text-white transition-colors z-20"
      >
        <ArrowLeft className="w-5 h-5" />
        Back to Home
      </Link>

      <div className="container mx-auto px-4 py-16 relative z-10">
        <div className="text-center mb-16">
          <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-600">
            {type.charAt(0).toUpperCase() + type.slice(1)} Analysis
          </h1>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            {type === 'combined'
              ? 'Analyze tweets using all available models for comprehensive insights into sentiment, emotions, and toxicity.'
              : `Deep dive into the ${type} aspects of tweets to understand their impact and context.`}
          </p>
        </div>

        <div className="flex justify-center">
          <AnalysisForm onSubmit={handleAnalysis} modelType={type} />
        </div>

        {loading && (
          <p className="mt-10 text-center text-blue-400 text-xl">Analyzing... Please wait.</p>
        )}

        {error && (
          <p className="mt-10 text-center text-red-500 text-xl">{error}</p>
        )}

        {result.length > 0 && (
          <div className="mt-10 space-y-6 max-w-3xl mx-auto">
            {result.map((tweet, idx) => (
              <TweetCard
                key={idx}
                tweet={{
                  content: tweet.content,
                  handle: tweet.handle || '@user',
                  timestamp: tweet.timestamp || new Date().toISOString(),
                  tweet_id: tweet.tweet_id || String(idx)
                }}
                analysis={{
                  sentiment: tweet.sentiment,
                  emotion: tweet.emotion,
                  toxicity: tweet.toxicity
                }}
                type={type}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Analysis