import { useState, useEffect } from 'react';
import { BackgroundTweets } from '../components/BackgroundTweets';
import { Link } from 'react-router-dom';
import { ArrowLeft, Trophy, Hash, User, Loader2, Medal } from 'lucide-react';

type LeaderboardEntry = {
  username?: string;
  hashtag?: string;
  count: number;
  rank: number;
};

type LeaderboardResponse = {
  leaderboard_type: string;
  category: string;
  results: LeaderboardEntry[];
};

const categories = [
  { id: 'positive', label: 'Most Positive', color: 'from-green-400 to-emerald-600', icon: '😊' },
  { id: 'negative', label: 'Most Negative', color: 'from-red-400 to-rose-600', icon: '😔' },
  { id: 'toxic', label: 'Most Toxic', color: 'from-orange-400 to-red-600', icon: '☢️' },
  { id: 'non_toxic', label: 'Most Non-Toxic', color: 'from-blue-400 to-indigo-600', icon: '🕊️' },
  { id: 'joy', label: 'Most Joyful', color: 'from-yellow-400 to-amber-600', icon: '🎉' },
  { id: 'sadness', label: 'Most Sad', color: 'from-purple-400 to-indigo-600', icon: '💔' },
  { id: 'anger', label: 'Most Angry', color: 'from-red-500 to-pink-600', icon: '😠' },
  { id: 'optimism', label: 'Most Optimistic', color: 'from-cyan-400 to-blue-600', icon: '🌟' },
];

const getRankIcon = (rank: number) => {
  switch (rank) {
    case 1:
      return <Medal className="w-6 h-6 text-yellow-400" />;
    case 2:
      return <Medal className="w-6 h-6 text-gray-300" />;
    case 3:
      return <Medal className="w-6 h-6 text-amber-700" />;
    default:
      return <span className="text-lg font-bold">{rank}</span>;
  }
};

export const Leaderboard = () => {
  const [type, setType] = useState<'username' | 'hashtag'>('username');
  const [category, setCategory] = useState('positive');
  const [data, setData] = useState<LeaderboardResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchLeaderboard = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `http://localhost:8000/api/leaderboard/?type=${type}&category=${category}&limit=10`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to fetch leaderboard data');
      }

      const jsonData = await response.json();
      setData(jsonData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLeaderboard();
  }, [type, category]);

  const selectedCategory = categories.find(c => c.id === category);

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

      <div className="container mx-auto px-4 py-16 relative z-10">
        <div className="text-center mb-12">
          <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-600">
            Twitter Analysis Leaderboard
          </h1>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            Discover trending users and hashtags across different sentiment categories
          </p>
        </div>

        <div className="flex flex-col items-center gap-8 mb-12">
          <div className="flex gap-4">
            <button
              onClick={() => setType('username')}
              className={`flex items-center gap-2 px-6 py-3 rounded-lg transition-colors ${
                type === 'username' ? 'bg-blue-500 text-white' : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
              }`}
            >
              <User className="w-5 h-5" />
              Users
            </button>
            <button
              onClick={() => setType('hashtag')}
              className={`flex items-center gap-2 px-6 py-3 rounded-lg transition-colors ${
                type === 'hashtag' ? 'bg-blue-500 text-white' : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
              }`}
            >
              <Hash className="w-5 h-5" />
              Hashtags
            </button>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {categories.map((cat) => (
              <button
                key={cat.id}
                onClick={() => setCategory(cat.id)}
                className={`px-6 py-3 rounded-lg transition-all transform hover:scale-105 ${
                  category === cat.id
                    ? `bg-gradient-to-r ${cat.color} text-white`
                    : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                }`}
              >
                <span className="text-xl mr-2">{cat.icon}</span>
                {cat.label}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div className="flex justify-center items-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
          </div>
        ) : error ? (
          <div className="text-center text-red-500 py-12">{error}</div>
        ) : data?.results.length === 0 ? (
          <div className="text-center text-gray-400 py-12">No data available for this category</div>
        ) : (
          <div className="max-w-3xl mx-auto">
            <div className="bg-gray-800/50 rounded-2xl backdrop-blur-sm border border-gray-700/50 overflow-hidden">
              <div className="grid grid-cols-12 gap-4 p-4 border-b border-gray-700/50 text-gray-400 font-medium">
                <div className="col-span-2 text-center">Rank</div>
                <div className="col-span-7">{type === 'username' ? 'User' : 'Hashtag'}</div>
                <div className="col-span-3 text-right">Count</div>
              </div>
              {data?.results.map((entry, index) => (
                <div
                  key={index}
                  className={`grid grid-cols-12 gap-4 p-4 items-center ${
                    index < 3 ? `bg-gradient-to-r ${selectedCategory?.color} bg-opacity-10` : ''
                  } hover:bg-gray-700/30 transition-colors`}
                >
                  <div className="col-span-2 flex justify-center">
                    {getRankIcon(entry.rank)}
                  </div>
                  <div className="col-span-7 font-semibold">
                    {entry.username || `#${entry.hashtag}`}
                  </div>
                  <div className="col-span-3 text-right">
                    <span className="bg-gray-700/50 px-3 py-1 rounded-full text-sm">
                      {entry.count.toLocaleString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Leaderboard;