import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { BackgroundTweets } from '../components/BackgroundTweets';
import { Brain, Heart, AlertTriangle, BarChart2, Trophy, History, MessageSquareText } from 'lucide-react';
import { getCookie } from '../utils/csrf';

export const Home = () => {
  const navigate = useNavigate();
  const [hoveredCard, setHoveredCard] = useState<string | null>(null);
  const [authStatus, setAuthStatus] = useState<{ is_authenticated: boolean, username?: string }>({ is_authenticated: false });

  const analysisTypes = [
    {
      id: 'combined',
      title: 'Tone Tracker',
      description: 'Analyze emotions, sentiment, and toxicity in tweets—uncovering joy, anger, and sadness, detecting toxicity, and gauging sentiment with precision!',
      icon: Brain,
      color: 'from-blue-500 to-purple-600',
      path: '/analysis/combined'
    },
    {
      id: 'emotional',
      title: 'Emotion Analysis',
      description: 'Identify the underlying emotions in tweets—joy, anger, sadness, or optimism.',
      icon: Heart,
      color: 'from-red-500 to-pink-600',
      path: '/analysis/emotional'
    },
    {
      id: 'toxicity',
      title: 'Toxicity Analysis',
      description: 'Detect and assess the toxicity level of tweets, distinguishing between toxic and non-toxic content.',
      icon: AlertTriangle,
      color: 'from-yellow-500 to-red-600',
      path: '/analysis/toxicity'
    },
    {
      id: 'sentimental',
      title: 'Sentiment Analysis',
      description: 'Gauge the overall sentiment of tweets as positive, negative, or neutral.',
      icon: BarChart2,
      color: 'from-green-500 to-teal-600',
      path: '/analysis/sentimental'
    },
    {
      id: 'livewall',
      title: 'Live Wall',
      description: 'Watch real-time analyzed tweets flow through our dynamic wall display.',
      icon: MessageSquareText,
      color: 'from-indigo-500 to-blue-600',
      path: '/livewall'
    },
    {
      id: 'leaderboard',
      title: 'Leaderboard',
      description: 'View top analyzed tweets and trending insights from our community of analysts.',
      icon: Trophy,
      color: 'from-amber-500 to-orange-600',
      path: '/leaderboard'
    }
  ];

  useEffect(() => {
    fetch('http://localhost:8000/api/auth/status/', {
      credentials: 'include',
      headers: {
        'X-CSRFToken': getCookie('csrftoken') || '',
      },
    })
      .then(res => res.json())
      .then(data => setAuthStatus(data))
      .catch(err => console.error('Auth status check failed:', err));
  }, []);

  const handleLogout = () => {
    fetch('http://localhost:8000/api/auth/logout/', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken') || '',
      }
    }).then(() => {
      setAuthStatus({ is_authenticated: false });
      navigate('/login');
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-black text-white relative overflow-hidden">
      <BackgroundTweets />

      {/* Navbar */}
      <nav className="relative z-20 py-4 px-6 border-b border-white/10 backdrop-blur-md bg-black/20">
        <div className="container mx-auto flex justify-between items-center">
          <Link to="/" className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-600">
            Analytica
          </Link>
          <div className="flex gap-4 items-center">
            {authStatus.is_authenticated ? (
              <>
                <span className="text-white/80">Hi, {authStatus.username}</span>
                <button
                  onClick={() => navigate('/history')}
                  className="px-4 py-2 rounded-lg bg-gradient-to-r from-purple-500 to-indigo-600 text-white hover:from-purple-600 hover:to-indigo-700 transition-all flex items-center gap-2"
                >
                  <History className="w-4 h-4" />
                  History
                </button>
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 rounded-lg border border-white/20 text-white hover:bg-white/10 transition-colors"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <button
                  onClick={() => navigate('/login')}
                  className="px-4 py-2 rounded-lg border border-white/20 text-white hover:bg-white/10 transition-colors"
                >
                  Login
                </button>
                <button
                  onClick={() => navigate('/signup')}
                  className="px-4 py-2 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 text-white hover:from-blue-600 hover:to-purple-700 transition-all"
                >
                  Sign Up
                </button>
              </>
            )}
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-4 py-16 relative z-10">
        <div className="text-center mb-16">
          <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-600">
            Welcome to Analytica!
          </h1>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            Analyze tweets using advanced AI models to understand emotions, detect toxicity, and measure sentiment.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {analysisTypes.map((type) => (
            <div
              key={type.id}
              className={`relative group cursor-pointer rounded-xl p-6 transition-all duration-300 transform hover:scale-105
                ${hoveredCard === type.id ? 'bg-white/10 backdrop-blur' : 'bg-white/5'}`}
              onMouseEnter={() => setHoveredCard(type.id)}
              onMouseLeave={() => setHoveredCard(null)}
              onClick={() => navigate(type.path)}
            >
              <div className={`absolute inset-0 rounded-xl bg-gradient-to-r ${type.color} opacity-0 group-hover:opacity-10 transition-opacity`} />
              <div className="flex items-start gap-4">
                <type.icon className="w-8 h-8" />
                <div>
                  <h3 className="text-xl font-semibold mb-2">{type.title}</h3>
                  <p className="text-gray-400">{type.description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Home;