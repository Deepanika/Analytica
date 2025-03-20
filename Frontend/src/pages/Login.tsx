import { useState } from 'react';
import { BackgroundTweets } from '../components/BackgroundTweets';
import { User, Lock, LogIn, Loader, Home } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';

export const Login = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState(''); // Changed from email to username
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(''); // For displaying login errors

  const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError(''); // Reset error state

    try {
      // Make API call to Django login endpoint
      const response = await axios.post(
        'http://localhost:8000/api/auth/login/',
        {
          username: username, // Use username instead of email
          password: password,
        },
        { withCredentials: true } // Ensure session cookies are sent/received
      );

      // On success, log the response and redirect to homepage
      console.log('Logged in successfully:', response.data);
      setLoading(false);
      navigate('/'); // Redirect to homepage route
    } catch (err) {
      // Handle errors (e.g., invalid credentials)
      setLoading(false);
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.error || 'An error occurred during login');
      } else {
        setError('An error occurred during login');
      }
      console.error('Login failed:', err);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-black text-white relative flex items-center justify-center overflow-hidden">
      <BackgroundTweets />
      
      {/* Back to Home Button */}
      <button 
        onClick={() => navigate('/')} 
        className="absolute top-6 left-6 z-20 flex items-center gap-2 px-4 py-2 rounded-lg border border-white/20 text-white hover:bg-white/10 transition-colors"
      >
        <Home className="w-4 h-4" /> Back to Home
      </button>
      
      <div className="w-full max-w-md bg-white/10 p-8 rounded-2xl border border-white/10 shadow-xl backdrop-blur-md relative z-10">
        <h1 className="text-4xl font-bold text-center bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-600 mb-6">
          Welcome Back
        </h1>
        <p className="text-gray-300 text-center mb-6">Log in to continue analyzing tweets</p>

        <form onSubmit={handleLogin} className="space-y-6">
          {/* Username Input */}
          <div className="relative">
            <User className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" /> {/* Changed icon from Mail to User */}
            <input
              type="text" // Changed from email to text
              placeholder="Enter your username" // Updated placeholder
              className="w-full pl-12 pr-4 py-3 rounded-lg bg-white/5 border border-white/10 focus:border-blue-500/50 focus:ring-2 focus:ring-blue-500/20 outline-none placeholder:text-gray-400 text-white"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>

          {/* Password Input */}
          <div className="relative">
            <Lock className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="password"
              placeholder="Enter your password"
              className="w-full pl-12 pr-4 py-3 rounded-lg bg-white/5 border border-white/10 focus:border-blue-500/50 focus:ring-2 focus:ring-blue-500/20 outline-none placeholder:text-gray-400 text-white"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          {/* Error Message */}
          {error && (
            <p className="text-red-400 text-center">{error}</p>
          )}

          {/* Login Button */}
          <button
            type="submit"
            className="w-full py-3 px-6 rounded-lg bg-gradient-to-r from-blue-500 to-blue-600 text-white font-medium hover:from-blue-600 hover:to-blue-700 transition-all duration-300 shadow-lg shadow-blue-500/30 hover:shadow-blue-500/40 transform hover:-translate-y-0.5 flex items-center justify-center gap-2"
            disabled={loading}
          >
            {loading ? <Loader className="w-5 h-5 animate-spin" /> : <LogIn className="w-5 h-5" />}
            {loading ? 'Logging in...' : 'Log In'}
          </button>
        </form>

        {/* Sign-up Link */}
        <p className="text-gray-400 text-center mt-6">
          Don't have an account?{' '}
          <Link to="/signup" className="text-blue-400 hover:text-blue-500 transition-colors">
            Sign up
          </Link>
        </p>
      </div>
    </div>
  );
};