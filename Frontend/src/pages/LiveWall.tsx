import { useState, useEffect, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Home, Pause, Play, Twitter, RefreshCw, ArrowLeft } from 'lucide-react';
import { BackgroundTweets } from '../components/BackgroundTweets';

interface Tweet {
  id: string;
  handle: string;
  content: string;
  timestamp: string;
  sentiment: string;
  toxicity: string;
  emotion: string;
}

export const LiveWall = () => {
  const navigate = useNavigate();
  const [tweets, setTweets] = useState<Tweet[]>([]);
  const [displayedTweets, setDisplayedTweets] = useState<Tweet[]>([]);
  const [isPaused, setIsPaused] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const indexRef = useRef(0);
  const [animatingTweetId, setAnimatingTweetId] = useState<string | null>(null);

  useEffect(() => {
    fetchLiveTweets();
  }, []);

  useEffect(() => {
    if (tweets.length === 0) return;

    const interval = setInterval(() => {
      if (!isPaused) {
        updateWall();
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [tweets, isPaused]);

  const fetchLiveTweets = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/livewall/');
      if (!response.ok) {
        const errorData = await response.json();
        setError(errorData.error || 'Failed to fetch live tweets.');
        return;
      }
      const data = await response.json();
      setTweets(data);
      setDisplayedTweets(data.slice(0, 6));
      indexRef.current = 6;
    } catch (err) {
      console.error('Error fetching live tweets:', err);
      setError('An unexpected error occurred while fetching live tweets.');
    }
  };

  const updateWall = () => {
    if (tweets.length === 0) return;

    const nextTweet = tweets[indexRef.current % tweets.length];
    indexRef.current++;

    setAnimatingTweetId(nextTweet.id);
    setTimeout(() => setAnimatingTweetId(null), 800);

    setDisplayedTweets((prev) => [nextTweet, ...prev.slice(0, 5)]);
  };

  const getAnalysisColor = (type: string, value: string) => {
    const baseClasses = 'px-3 py-1 rounded-full text-sm font-medium backdrop-blur-sm ';

    if (type === 'sentiment') {
      if (value === 'Positive') return baseClasses + 'bg-gradient-to-r from-green-500/30 to-teal-600/30 text-teal-200 border border-teal-500/30';
      if (value === 'Negative') return baseClasses + 'bg-gradient-to-r from-red-500/30 to-rose-600/30 text-rose-200 border border-rose-500/30';
      return baseClasses + 'bg-gradient-to-r from-blue-500/30 to-indigo-600/30 text-indigo-200 border border-indigo-500/30';
    } else if (type === 'toxicity') {
      return value === 'offensive'
        ? baseClasses + 'bg-gradient-to-r from-yellow-500/30 to-red-600/30 text-red-200 border border-red-500/30'
        : baseClasses + 'bg-gradient-to-r from-green-500/30 to-teal-600/30 text-teal-200 border border-teal-500/30';
    } else if (type === 'emotion') {
      switch (value.toLowerCase()) {
        case 'anger': return baseClasses + 'bg-gradient-to-r from-red-500/30 to-orange-600/30 text-orange-200 border border-orange-500/30';
        case 'joy': return baseClasses + 'bg-gradient-to-r from-yellow-500/30 to-amber-600/30 text-amber-200 border border-amber-500/30';
        case 'optimism': return baseClasses + 'bg-gradient-to-r from-green-500/30 to-teal-600/30 text-teal-200 border border-teal-500/30';
        case 'sadness': return baseClasses + 'bg-gradient-to-r from-blue-500/30 to-cyan-600/30 text-cyan-200 border border-cyan-500/30';
        default: return baseClasses + 'bg-gradient-to-r from-gray-500/30 to-slate-600/30 text-gray-200 border border-gray-500/30';
      }
    }
    return baseClasses + 'bg-gradient-to-r from-gray-500/30 to-slate-600/30 text-gray-200 border border-gray-500/30';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-black text-white relative overflow-hidden">
      <BackgroundTweets />
      <Link
        to="/"
        className="absolute top-6 left-6 flex items-center gap-2 text-white/60 hover:text-white transition-colors z-20"
      >
        <ArrowLeft className="w-5 h-5" />
        Back to Home
      </Link>

      <div className="relative z-10">
        {/* Header */}
        <nav className="sticky top-0 border-b border-white/10 backdrop-blur-md bg-black/20">
          <div className="container mx-auto px-6 py-4">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-3">
                <Twitter className="w-8 h-8 text-blue-400" />
                <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-600">
                  Live Tweet Wall
                </h1>
              </div>
              <div className="flex gap-4">
                <button
                  onClick={() => setIsPaused(!isPaused)}
                  className="px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 transition-all duration-300 flex items-center gap-2 group border border-white/10"
                >
                  {isPaused ? (
                    <Play className="w-4 h-4 text-green-400 group-hover:scale-110 transition-transform" />
                  ) : (
                    <Pause className="w-4 h-4 text-yellow-400 group-hover:scale-110 transition-transform" />
                  )}
                  {isPaused ? 'Resume' : 'Pause'}
                </button>
                <button
                  onClick={() => fetchLiveTweets()}
                  className="px-4 py-2 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 transition-all duration-300 flex items-center gap-2 group"
                >
                  <RefreshCw className="w-4 h-4 group-hover:rotate-180 transition-transform duration-500" />
                  Refresh
                </button>
              </div>
            </div>
          </div>
        </nav>

        {/* Tweet Wall */}
        <div className="container mx-auto px-4 py-8">
          <div className="flex flex-col gap-4">
            {displayedTweets.map((tweet, index) => (
              <div
                key={`${tweet.id}-${index}`}
                className={`relative group bg-white/5 backdrop-blur rounded-xl p-6 border border-white/10 
                  transform transition-all duration-500 hover:scale-[1.01] hover:bg-white/10
                  ${animatingTweetId === tweet.id ? 'tweet-enter' : ''}`}
              >
                <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-blue-500 to-purple-600 opacity-0 group-hover:opacity-5 transition-opacity" />
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg">
                    <span className="text-lg font-bold">{tweet.handle.charAt(1).toUpperCase()}</span>
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg">{tweet.handle}</h3>
                    <p className="text-sm text-gray-400">{tweet.timestamp}</p>
                    <p className="mt-3 text-gray-300 leading-relaxed">{tweet.content}</p>
                    <div className="mt-4 flex flex-wrap gap-2">
                      {['sentiment', 'toxicity', 'emotion'].map((type) => (
                        tweet[type as keyof Tweet] && (
                          <span
                            key={type}
                            className={getAnalysisColor(type, tweet[type as keyof Tweet])}
                          >
                            {type.charAt(0).toUpperCase() + type.slice(1)}: {tweet[type as keyof Tweet]}
                          </span>
                        )
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LiveWall;