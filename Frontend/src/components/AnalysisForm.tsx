import React, { useState } from 'react';
import { Search, Hash, User, BarChart } from 'lucide-react';

interface AnalysisFormProps {
  onSubmit: (data: { query: string; tweetCount: number }) => void;
  modelType: 'combined' | 'emotional' | 'toxicity' | 'sentimental';
}

export const AnalysisForm: React.FC<AnalysisFormProps> = ({ onSubmit, modelType }) => {
  const [query, setQuery] = useState('');
  const [tweetCount, setTweetCount] = useState(10);
  const [queryType, setQueryType] = useState<'hashtag' | 'username'>('hashtag');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ query, tweetCount });
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-md backdrop-blur-xl bg-white/5 p-8 rounded-2xl border border-white/10 shadow-2xl">
      <div className="space-y-6">
        <div className="space-y-4">
          <div className="flex gap-2 p-1 bg-white/5 rounded-lg">
            <button
              type="button"
              onClick={() => setQueryType('hashtag')}
              className={`flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-lg transition-all duration-300 ${
                queryType === 'hashtag'
                  ? 'bg-blue-500 shadow-lg shadow-blue-500/30'
                  : 'hover:bg-white/5'
              }`}
            >
              <Hash className="w-4 h-4" />
              <span>Hashtag</span>
            </button>
            <button
              type="button"
              onClick={() => setQueryType('username')}
              className={`flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-lg transition-all duration-300 ${
                queryType === 'username'
                  ? 'bg-blue-500 shadow-lg shadow-blue-500/30'
                  : 'hover:bg-white/5'
              }`}
            >
              <User className="w-4 h-4" />
              <span>Username</span>
            </button>
          </div>
          <div className="relative">
            <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
              {queryType === 'hashtag' ? (
                <Hash className="w-5 h-5 text-white/40" />
              ) : (
                <User className="w-5 h-5 text-white/40" />
              )}
            </div>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={queryType === 'hashtag' ? 'Enter hashtag...' : 'Enter username...'}
              className="w-full pl-12 pr-4 py-4 rounded-lg bg-white/5 border border-white/10 focus:border-blue-500/50 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all placeholder:text-white/30 text-white"
              required
            />
            <div className="absolute inset-y-0 right-4 flex items-center pointer-events-none">
              <Search className="w-5 h-5 text-white/20" />
            </div>
          </div>
        </div>

        <div className="space-y-2">
          <label className="flex items-center gap-2 text-sm font-medium text-white/60">
            <BarChart className="w-4 h-4" />
            Number of tweets to analyze
          </label>
          <input
            type="range"
            min="1"
            max="100"
            value={tweetCount}
            onChange={(e) => setTweetCount(Number(e.target.value))}
            className="w-full h-2 bg-white/5 rounded-lg appearance-none cursor-pointer accent-blue-500"
          />
          <div className="flex justify-between text-sm text-white/40">
            <span>1</span>
            <span className="text-white">{tweetCount} tweets</span>
            <span>100</span>
          </div>
        </div>

        <button
          type="submit"
          className="w-full py-4 px-6 rounded-lg bg-gradient-to-r from-blue-500 to-blue-600 text-white font-medium hover:from-blue-600 hover:to-blue-700 transition-all duration-300 shadow-lg shadow-blue-500/30 hover:shadow-blue-500/40 transform hover:-translate-y-0.5"
        >
          Analyze {modelType === 'combined' ? 'All Aspects !' : '!'}
        </button>
      </div>
    </form>
  );
};