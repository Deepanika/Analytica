import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { BackgroundTweets } from '../components/BackgroundTweets';
import { Home, ArrowLeft, ArrowRight, Trophy, ThumbsUp, Heart, AlertTriangle } from 'lucide-react';

// Define types for our tweet data
interface AnalyzedTweet {
  id: string;
  text: string;
  author: string;
  profileImage: string;
  date: string;
  likes: number;
  emotion: {
    joy: number;
    sadness: number;
    anger: number;
    optimism: number;
  };
  toxicity: number;
  sentiment: number;
  views: number;
}

export const Leaderboard = () => {
  const navigate = useNavigate();
  const [tweets, setTweets] = useState<AnalyzedTweet[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [filter, setFilter] = useState<'sentiment' | 'toxicity' | 'popularity'>('popularity');
  
  const tweetsPerPage = 5;

  useEffect(() => {
    const fetchTweets = async () => {
      setLoading(true);
      try {
        // Replace with your actual API endpoint
        const response = await fetch('/api/analyzed-tweets');
        
        if (!response.ok) {
          throw new Error('Failed to fetch tweets');
        }
        
        const data = await response.json();
        setTweets(data);
      } catch (err) {
        console.error('Error fetching tweets:', err);
        setError('Failed to load leaderboard data. Please try again later.');
        
        // For demo purposes, add some mock data when the API call fails
        setTweets(getMockTweets());
      } finally {
        setLoading(false);
      }
    };
    
    fetchTweets();
  }, []);

  // Get sorted tweets based on the filter
  const getSortedTweets = () => {
    if (filter === 'sentiment') {
      return [...tweets].sort((a, b) => b.sentiment - a.sentiment);
    } else if (filter === 'toxicity') {
      return [...tweets].sort((a, b) => a.toxicity - b.toxicity); // Lower toxicity is better
    } else {
      return [...tweets].sort((a, b) => b.views - a.views);
    }
  };

  const sortedTweets = getSortedTweets();
  
  // Calculate pagination
  const indexOfLastTweet = currentPage * tweetsPerPage;
  const indexOfFirstTweet = indexOfLastTweet - tweetsPerPage;
  const currentTweets = sortedTweets.slice(indexOfFirstTweet, indexOfLastTweet);
  const totalPages = Math.ceil(tweets.length / tweetsPerPage);

  const nextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    }
  };

  const prevPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  // Helper function to determine sentiment display
  const getSentimentDisplay = (sentiment: number) => {
    if (sentiment > 0.5) return { text: 'Positive', color: 'text-green-400' };
    if (sentiment < -0.3) return { text: 'Negative', color: 'text-red-400' };
    return { text: 'Neutral', color: 'text-blue-400' };
  };

  // Helper function to format numbers
  const formatNumber = (num: number) => {
    return new Intl.NumberFormat().format(num);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-black text-white relative overflow-hidden">
      <BackgroundTweets />
      
      {/* Back to Home Button */}
      <button 
        onClick={() => navigate('/')} 
        className="absolute top-6 left-6 z-20 flex items-center gap-2 px-4 py-2 rounded-lg border border-white/20 text-white hover:bg-white/10 transition-colors"
      >
        <Home className="w-4 h-4" /> Back to Home
      </button>
      
      <div className="container mx-auto px-4 py-20 relative z-10">
        <div className="text-center mb-10">
        <h1 className="text-4xl md:text-5xl font-bold mb-4 flex items-center justify-center gap-3">
            <Trophy className="text-blue-400 w-10 h-10" />
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-600">
                Tweet Analysis Leaderboard
            </span>
        </h1>
        <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            Discover the most analyzed and impactful tweets on our platform
        </p>
        </div>
        
        {/* Filter Controls */}
        <div className="flex justify-center gap-4 mb-8">
          <button 
            onClick={() => setFilter('popularity')}
            className={`px-4 py-2 rounded-lg transition-colors ${filter === 'popularity' 
              ? 'bg-gradient-to-r from-amber-500 to-orange-600 text-white' 
              : 'bg-white/10 hover:bg-white/20'}`}
          >
            Most Popular
          </button>
          <button 
            onClick={() => setFilter('sentiment')}
            className={`px-4 py-2 rounded-lg transition-colors ${filter === 'sentiment' 
              ? 'bg-gradient-to-r from-green-500 to-teal-600 text-white' 
              : 'bg-white/10 hover:bg-white/20'}`}
          >
            Most Positive
          </button>
          <button 
            onClick={() => setFilter('toxicity')}
            className={`px-4 py-2 rounded-lg transition-colors ${filter === 'toxicity' 
              ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white' 
              : 'bg-white/10 hover:bg-white/20'}`}
          >
            Least Toxic
          </button>
        </div>

        {/* Leaderboard Content */}
        {loading ? (
          <div className="flex items-center justify-center py-16">
            <div className="w-12 h-12 border-4 border-t-blue-500 border-r-transparent border-b-blue-500 border-l-transparent rounded-full animate-spin"></div>
          </div>
        ) : error ? (
          <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-4 text-center text-red-200">
            {error}
          </div>
        ) : (
          <>
            <div className="space-y-6 max-w-4xl mx-auto">
              {currentTweets.map((tweet, index) => {
                const sentimentInfo = getSentimentDisplay(tweet.sentiment);
                const rank = indexOfFirstTweet + index + 1;
                
                return (
                  <div 
                    key={tweet.id}
                    className="bg-white/10 backdrop-blur-sm rounded-xl border border-white/10 p-5 hover:bg-white/15 transition-colors"
                  >
                    <div className="flex items-start gap-4">
                      {/* Rank */}
                      <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                        rank === 1 ? 'bg-amber-400 text-black' :
                        rank === 2 ? 'bg-gray-300 text-black' :
                        rank === 3 ? 'bg-amber-700 text-white' :
                        'bg-white/20 text-white'
                      }`}>
                        {rank}
                      </div>
                      
                      {/* Tweet content */}
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <img 
                            src={tweet.profileImage || `https://ui-avatars.com/api/?name=${tweet.author}&background=random`} 
                            alt={tweet.author}
                            className="w-6 h-6 rounded-full"
                          />
                          <span className="font-semibold text-sm">{tweet.author}</span>
                          <span className="text-gray-400 text-xs">• {tweet.date}</span>
                        </div>
                        
                        <p className="text-gray-200 mb-3">{tweet.text}</p>
                        
                        <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-sm">
                          <div className="flex items-center gap-1">
                            <ThumbsUp className="w-4 h-4 text-blue-400" />
                            <span>{formatNumber(tweet.likes)}</span>
                          </div>
                          
                          <div className="flex items-center gap-1">
                            <span className={sentimentInfo.color}>Sentiment:</span> 
                            <span className={sentimentInfo.color}>{sentimentInfo.text}</span>
                          </div>
                          
                          <div className="flex items-center gap-1">
                            <AlertTriangle className={`w-4 h-4 ${tweet.toxicity > 0.5 ? 'text-red-400' : 'text-green-400'}`} />
                            <span>Toxicity: {Math.round(tweet.toxicity * 100)}%</span>
                          </div>
                          
                          <div className="flex items-center gap-1 ml-auto">
                            <Heart className="w-4 h-4 text-red-400" />
                            <span>
                              {
                                Object.entries(tweet.emotion)
                                  .sort(([, a], [, b]) => b - a)[0][0]
                                  .charAt(0).toUpperCase() + 
                                Object.entries(tweet.emotion)
                                  .sort(([, a], [, b]) => b - a)[0][0]
                                  .slice(1)
                              }
                            </span>
                          </div>
                          
                          <div>
                            <span className="text-amber-400">
                              {formatNumber(tweet.views)} views
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
            
            {/* Pagination */}
            {tweets.length > tweetsPerPage && (
              <div className="flex items-center justify-center gap-4 mt-8">
                <button 
                  onClick={prevPage}
                  disabled={currentPage === 1}
                  className={`p-2 rounded-lg ${currentPage === 1 ? 'bg-white/5 text-gray-500 cursor-not-allowed' : 'bg-white/10 hover:bg-white/20'}`}
                >
                  <ArrowLeft className="w-5 h-5" />
                </button>
                
                <span className="text-gray-300">
                  Page {currentPage} of {totalPages}
                </span>
                
                <button 
                  onClick={nextPage}
                  disabled={currentPage === totalPages}
                  className={`p-2 rounded-lg ${currentPage === totalPages ? 'bg-white/5 text-gray-500 cursor-not-allowed' : 'bg-white/10 hover:bg-white/20'}`}
                >
                  <ArrowRight className="w-5 h-5" />
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

// Mock data function for demonstration purposes
function getMockTweets(): AnalyzedTweet[] {
  return [
    {
      id: '1',
      text: 'Artificial intelligence is making incredible strides. The future looks bright for technology innovation!',
      author: 'TechOptimist',
      profileImage: '',
      date: 'Mar 10, 2025',
      likes: 1842,
      emotion: { joy: 0.75, sadness: 0.05, anger: 0.05, optimism: 0.85 },
      toxicity: 0.02,
      sentiment: 0.85,
      views: 42500
    },
    {
      id: '2',
      text: 'Just watched the sunset at the beach. Nature never fails to amaze me with its beautiful colors! 🌅',
      author: 'NatureLover',
      profileImage: '',
      date: 'Mar 12, 2025',
      likes: 2103,
      emotion: { joy: 0.9, sadness: 0.02, anger: 0.01, optimism: 0.78 },
      toxicity: 0.01,
      sentiment: 0.92,
      views: 38200
    },
    {
      id: '3',
      text: 'The new policy changes are concerning. We need to pay attention to how this affects everyday citizens.',
      author: 'PolicyWatcher',
      profileImage: '',
      date: 'Mar 8, 2025',
      likes: 1504,
      emotion: { joy: 0.1, sadness: 0.45, anger: 0.3, optimism: 0.25 },
      toxicity: 0.15,
      sentiment: -0.2,
      views: 35600
    },
    {
      id: '4',
      text: 'This game was absolutely terrible. Worst $60 I\'ve ever spent on a broken, unfinished product.',
      author: 'GamerReviewer',
      profileImage: '',
      date: 'Mar 11, 2025',
      likes: 892,
      emotion: { joy: 0.05, sadness: 0.3, anger: 0.8, optimism: 0.05 },
      toxicity: 0.45,
      sentiment: -0.75,
      views: 29800
    },
    {
      id: '5',
      text: 'My new book is finally available! Thanks to everyone who supported me on this journey. #NewRelease',
      author: 'AuthorJD',
      profileImage: '',
      date: 'Mar 9, 2025',
      likes: 1267,
      emotion: { joy: 0.85, sadness: 0.05, anger: 0.02, optimism: 0.9 },
      toxicity: 0.01,
      sentiment: 0.88,
      views: 31200
    },
    {
      id: '6',
      text: 'The latest update to this app is horrible. Everything is broken and my data is missing!',
      author: 'TechUser',
      profileImage: '',
      date: 'Mar 7, 2025',
      likes: 723,
      emotion: { joy: 0.02, sadness: 0.35, anger: 0.85, optimism: 0.05 },
      toxicity: 0.4,
      sentiment: -0.7,
      views: 18600
    },
    {
      id: '7',
      text: 'Just finished a 5K run and beat my personal record! Hard work pays off! 🏃‍♂️',
      author: 'FitnessJunkie',
      profileImage: '',
      date: 'Mar 13, 2025',
      likes: 891,
      emotion: { joy: 0.9, sadness: 0.02, anger: 0.01, optimism: 0.95 },
      toxicity: 0.01,
      sentiment: 0.9,
      views: 12800
    },
    {
      id: '8',
      text: 'This conference is amazing! Learning so much from incredible speakers. #TechConf2025',
      author: 'DevEnthusiast',
      profileImage: '',
      date: 'Mar 5, 2025',
      likes: 654,
      emotion: { joy: 0.8, sadness: 0.05, anger: 0.02, optimism: 0.85 },
      toxicity: 0.05,
      sentiment: 0.75,
      views: 9300
    }
  ];
}