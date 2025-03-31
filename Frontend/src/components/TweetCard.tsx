import { Twitter } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface Tweet {
  content: string;
  handle: string;
  timestamp: string;
  tweet_id: string;
  translated_content?: string; // Added optional translated_content field
}

interface TweetCardProps {
  tweet: Tweet;
  analysis: {
    sentiment?: string;
    emotion?: string;
    toxicity?: string;
  };
  type: 'combined' | 'emotional' | 'toxicity' | 'sentimental';
}

export const TweetCard = ({ tweet, analysis, type }: TweetCardProps) => {
  const formattedDate = formatDistanceToNow(new Date(tweet.timestamp), { addSuffix: true });

  return (
    <div className="bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/10 hover:border-white/20 transition-all">
      <div className="flex items-start gap-4">
        {/* Profile Picture - Using a placeholder gradient */}
        <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-400 to-purple-600 flex items-center justify-center">
          <Twitter className="w-6 h-6 text-white" />
        </div>

        <div className="flex-1">
          {/* Tweet Header */}
          <div className="flex items-center gap-2 mb-1">
            <span className="font-bold text-white">{tweet.handle}</span>
            <span className="text-gray-400">{formattedDate}</span>
          </div>

          {/* Tweet Content */}
          <p className="text-white/90 mb-4 text-lg">{tweet.content}</p>

          {/* Translated Content */}
          {tweet.translated_content && (
            <div className="mt-2 mb-4">
              <p className="text-white/60 text-sm">Translation:</p>
              <p className="text-white/80 text-lg">{tweet.translated_content}</p>
            </div>
          )}

          {/* Analysis Results */}
          <div className="grid gap-3">
            {type === 'combined' && (
              <>
                <AnalysisItem label="Sentiment" value={analysis.sentiment} color="blue" />
                <AnalysisItem label="Emotion" value={analysis.emotion} color="purple" />
                <AnalysisItem label="Toxicity" value={analysis.toxicity} color="pink" />
              </>
            )}
            {type === 'sentimental' && (
              <AnalysisItem label="Sentiment" value={analysis.sentiment} color="blue" />
            )}
            {type === 'emotional' && (
              <AnalysisItem label="Emotion" value={analysis.emotion} color="purple" />
            )}
            {type === 'toxicity' && (
              <AnalysisItem label="Toxicity" value={analysis.toxicity} color="pink" />
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

interface AnalysisItemProps {
  label: string;
  value?: string;
  color: 'blue' | 'purple' | 'pink';
}

const AnalysisItem = ({ label, value, color }: AnalysisItemProps) => {
  const colorClasses = {
    blue: 'from-blue-400/20 to-blue-600/20 border-blue-500/30',
    purple: 'from-purple-400/20 to-purple-600/20 border-purple-500/30',
    pink: 'from-pink-400/20 to-pink-600/20 border-pink-500/30',
  };

  return (
    <div className={`bg-gradient-to-r ${colorClasses[color]} p-3 rounded-lg border`}>
      <span className="text-white/60 text-sm">{label}:</span>
      <span className="ml-2 text-white font-medium">{value}</span>
    </div>
  );
};