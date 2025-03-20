import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { getCookie } from '../utils/csrf';
import { Calendar, Search, ArrowRight, ArrowLeft } from 'lucide-react';
import { BackgroundTweets } from '../components/BackgroundTweets';

interface HistoryEntry {
  id: number;
  search_query: string;
  search_type: string;
  analysis_type: string;
  timestamp: string;
}

interface Tweet {
  id: number;
  handle: string;
  content: string;
  timestamp: string;
  sentiment?: string;
  toxicity?: number;
  emotion?: string;
}

const getAnalysisDisplay = (tweet: Tweet, analysisType: string) => {
  switch (analysisType) {
    case 'combined':
      return (
        <>
          {tweet.sentiment && (
            <span className="px-3 py-1 rounded-full text-sm bg-green-500/20 text-green-400">
              Sentiment: {tweet.sentiment}
            </span>
          )}
          {tweet.toxicity && (
            <span className="px-3 py-1 rounded-full text-sm bg-red-500/20 text-red-400">
              Toxicity: {tweet.toxicity}
            </span>
          )}
          {tweet.emotion && (
            <span className="px-3 py-1 rounded-full text-sm bg-purple-500/20 text-purple-400">
              Emotion: {tweet.emotion}
            </span>
          )}
        </>
      );
    case 'sentiment':
      return tweet.sentiment && (
        <span className="px-3 py-1 rounded-full text-sm bg-green-500/20 text-green-400">
          Sentiment: {tweet.sentiment}
        </span>
      );
    case 'toxicity':
      return tweet.toxicity && (
        <span className="px-3 py-1 rounded-full text-sm bg-red-500/20 text-red-400">
          Toxicity: {tweet.toxicity}
        </span>
      );
    case 'emotion':
      return tweet.emotion && (
        <span className="px-3 py-1 rounded-full text-sm bg-purple-500/20 text-purple-400">
          Emotion: {tweet.emotion}
        </span>
      );
    default:
      return null;
  }
};

export const History = () => {
  const navigate = useNavigate();
  const [searchHistory, setSearchHistory] = useState<HistoryEntry[]>([]);
  const [selectedHistory, setSelectedHistory] = useState<number | null>(null);
  const [tweets, setTweets] = useState<Tweet[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSearchHistory();
  }, []);

  const fetchSearchHistory = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/history/', {
        credentials: 'include',
        headers: {
          'X-CSRFToken': getCookie('csrftoken') || '',
        },
      });

      if (response.status === 401) {
        navigate('/login');
        return;
      }

      const data = await response.json();
      setSearchHistory(data.search_history);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching history:', error);
      setLoading(false);
    }
  };

  const fetchHistoryTweets = async (historyId: number) => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/api/history/tweets/${historyId}/`, {
        credentials: 'include',
        headers: {
          'X-CSRFToken': getCookie('csrftoken') || '',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setTweets(data.tweets);
        setSelectedHistory(historyId);
      }
    } catch (error) {
      console.error('Error fetching tweets:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getAnalysisTypeColor = (type: string) => {
    const colors = {
      sentiment: 'bg-green-500',
      toxicity: 'bg-red-500',
      emotion: 'bg-purple-500',
      combined: 'bg-blue-500',
    };
    return colors[type as keyof typeof colors] || 'bg-gray-500';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 to-black text-white flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-black text-white p-8">
      <BackgroundTweets />
      <Link
        to="/"
        className="absolute top-6 left-6 flex items-center gap-2 text-white/60 hover:text-white transition-colors z-20"
      >
        <ArrowLeft className="w-5 h-5" />
        Back to Home
      </Link>
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold mb-8 bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-pink-600">
          Search History
        </h1>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* History List */}
          <div className="lg:col-span-1 space-y-4">
            {searchHistory.map((entry) => (
              <div
                key={entry.id}
                className={`p-4 rounded-lg cursor-pointer transition-all ${
                  selectedHistory === entry.id
                    ? 'bg-white/20 backdrop-blur'
                    : 'bg-white/10 hover:bg-white/15'
                }`}
                onClick={() => fetchHistoryTweets(entry.id)}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${getAnalysisTypeColor(entry.analysis_type)}`}>
                    {entry.analysis_type.charAt(0).toUpperCase() + entry.analysis_type.slice(1)}
                  </span>
                  <div className="flex items-center text-sm text-gray-400">
                    <Calendar className="w-4 h-4 mr-1" />
                    {formatDate(entry.timestamp)}
                  </div>
                </div>
                <div className="flex items-center gap-2 text-lg font-medium">
                  <Search className="w-5 h-5" />
                  <span>{entry.search_query}</span>
                </div>
                <div className="mt-1 text-sm text-gray-400">
                  Search type: {entry.search_type}
                </div>
              </div>
            ))}
          </div>

          {/* Tweet Results */}
          <div className="lg:col-span-2">
            {selectedHistory ? (
              <div className="space-y-4">
                <h2 className="text-2xl font-semibold mb-4">Analysis Results</h2>
                {tweets.map((tweet) => (
                  <div key={tweet.id} className="p-4 rounded-lg bg-white/10 backdrop-blur">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="font-medium text-purple-400">{tweet.handle}</span>
                      <span className="text-sm text-gray-400">{formatDate(tweet.timestamp)}</span>
                    </div>
                    <p className="text-gray-200 mb-3">{tweet.content}</p>
                    <div className="flex flex-wrap gap-3">
                      {getAnalysisDisplay(
                        tweet,
                        searchHistory.find((entry) => entry.id === selectedHistory)?.analysis_type || ''
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="h-full flex items-center justify-center text-gray-400">
                <div className="text-center">
                  <ArrowRight className="w-12 h-12 mx-auto mb-4" />
                  <p>Select a search history entry to view the analysis results</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};