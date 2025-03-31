import React from 'react';
import { X } from 'lucide-react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement } from 'chart.js';
import { Pie, Bar } from 'react-chartjs-2';

ChartJS.register(ArcElement, CategoryScale, LinearScale, BarElement, Tooltip, Legend);

interface Tweet {
  sentiment?: string;
  emotion?: string;
  toxicity?: string;
}

interface AnalyticsModalProps {
  isOpen: boolean;
  onClose: () => void;
  tweets: Tweet[];
  type?: 'combined' | 'emotional' | 'toxicity' | 'sentimental' | string;
}

export const AnalyticsModal: React.FC<AnalyticsModalProps> = ({ isOpen, onClose, tweets, type = 'combined' }) => {
  if (!isOpen) return null;

  const calculateStats = () => {
    const stats = {
      sentiment: { positive: 0, neutral: 0, negative: 0 },
      emotion: { anger: 0, joy: 0, optimism: 0, sadness: 0 },
      toxicity: { offensive: 0, 'not-offensive': 0 }
    };

    tweets.forEach(tweet => {
      if (tweet.sentiment) stats.sentiment[tweet.sentiment.toLowerCase() as keyof typeof stats.sentiment]++;
      if (tweet.emotion) stats.emotion[tweet.emotion.toLowerCase() as keyof typeof stats.emotion]++;
      if (tweet.toxicity) stats.toxicity[tweet.toxicity.toLowerCase() as keyof typeof stats.toxicity]++;
    });

    return stats;
  };

  const stats = calculateStats();

  const shouldShowSentiment = type === 'combined' || type === 'sentimental' || type === 'sentiment';
  const shouldShowEmotion = type === 'combined' || type === 'emotional' || type === 'emotion';
  const shouldShowToxicity = type === 'combined' || type === 'toxicity';

  const chartOptions = {
    plugins: {
      legend: {
        position: 'bottom' as const,
        labels: {
          padding: 20,
          font: {
            size: 12
          },
          color: 'rgb(255, 255, 255)'
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        padding: 12,
        titleFont: {
          size: 14
        },
        bodyFont: {
          size: 13
        },
        callbacks: {
          label: function(context: any) {
            const value = context.raw;
            const total = context.dataset.data.reduce((a: number, b: number) => a + b, 0);
            const percentage = ((value / total) * 100).toFixed(1);
            return `${context.label}: ${value} (${percentage}%)`;
          }
        }
      }
    },
    maintainAspectRatio: false
  };

  const sentimentData = {
    labels: ['Positive', 'Neutral', 'Negative'],
    datasets: [{
      data: [stats.sentiment.positive, stats.sentiment.neutral, stats.sentiment.negative],
      backgroundColor: ['#10B981', '#6B7280', '#EF4444'],
      borderColor: ['rgba(16, 185, 129, 0.2)', 'rgba(107, 114, 128, 0.2)', 'rgba(239, 68, 68, 0.2)'],
      borderWidth: 2,
    }]
  };

  const emotionData = {
    labels: ['Anger', 'Joy', 'Optimism', 'Sadness'],
    datasets: [{
      data: [stats.emotion.anger, stats.emotion.joy, stats.emotion.optimism, stats.emotion.sadness],
      backgroundColor: ['#DC2626', '#FBBF24', '#3B82F6', '#6366F1'],
      borderColor: ['rgba(220, 38, 38, 0.2)', 'rgba(251, 191, 36, 0.2)', 'rgba(59, 130, 246, 0.2)', 'rgba(99, 102, 241, 0.2)'],
      borderWidth: 2,
    }]
  };

  const toxicityData = {
    labels: ['Offensive', 'Not Offensive'],
    datasets: [{
      data: [stats.toxicity.offensive, stats.toxicity['not-offensive']],
      backgroundColor: ['#F43F5E', '#22C55E'],
      borderColor: ['rgba(244, 63, 94, 0.2)', 'rgba(34, 197, 94, 0.2)'],
      borderWidth: 2,
    }]
  };

  const getGridCols = () => {
    const count = [shouldShowSentiment, shouldShowEmotion, shouldShowToxicity].filter(Boolean).length;
    if (count === 1) return 'grid-cols-1';
    if (count === 2) return 'grid-cols-1 md:grid-cols-2';
    return 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3';
  };

  const StatCard = ({ title, stats, total }: { title: string; stats: Record<string, number>; total: number }) => (
    <div className="bg-white/5 rounded-lg p-4 backdrop-blur-sm">
      <h4 className="font-semibold text-lg mb-3 text-white/90">{title}</h4>
      <div className="space-y-2">
        {Object.entries(stats).map(([key, value]) => {
          const percentage = ((value / total) * 100).toFixed(1);
          return (
            <div key={key} className="flex items-center justify-between">
              <span className="capitalize text-white/80">{key.replace('-', ' ')}</span>
              <div className="flex items-center gap-2">
                <span className="text-white/60">{value}</span>
                <span className="text-sm text-white/40">({percentage}%)</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 rounded-xl w-full max-w-5xl max-h-[90vh] overflow-y-auto border border-white/10">
        <div className="sticky top-0 bg-gray-900/95 backdrop-blur-sm border-b border-white/10 p-6 flex justify-between items-center">
          <h2 className="text-2xl font-bold text-white">Tweet Analysis Dashboard</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/10 rounded-full transition-colors"
            aria-label="Close"
          >
            <X className="w-6 h-6 text-white/80" />
          </button>
        </div>

        <div className="p-6 space-y-8">
          <div className={`grid ${getGridCols()} gap-6`}>
            {shouldShowSentiment && (
              <div className="bg-white/5 p-6 rounded-lg backdrop-blur-sm">
                <h3 className="text-lg font-semibold mb-4 text-white/90">Sentiment Distribution</h3>
                <div className="h-[300px]">
                  <Pie data={sentimentData} options={chartOptions} />
                </div>
              </div>
            )}

            {shouldShowEmotion && (
              <div className="bg-white/5 p-6 rounded-lg backdrop-blur-sm">
                <h3 className="text-lg font-semibold mb-4 text-white/90">Emotion Analysis</h3>
                <div className="h-[300px]">
                  <Pie data={emotionData} options={chartOptions} />
                </div>
              </div>
            )}

            {shouldShowToxicity && (
              <div className="bg-white/5 p-6 rounded-lg backdrop-blur-sm">
                <h3 className="text-lg font-semibold mb-4 text-white/90">Toxicity Analysis</h3>
                <div className="h-[300px]">
                  <Pie data={toxicityData} options={chartOptions} />
                </div>
              </div>
            )}
          </div>

          <div className="grid gap-6 mt-8">
            <h3 className="text-xl font-semibold text-white/90">Detailed Statistics</h3>
            <div className={`grid ${getGridCols()} gap-6`}>
              {shouldShowSentiment && (
                <StatCard 
                  title="Sentiment Stats" 
                  stats={stats.sentiment} 
                  total={tweets.length} 
                />
              )}
              {shouldShowEmotion && (
                <StatCard 
                  title="Emotion Stats" 
                  stats={stats.emotion} 
                  total={tweets.length} 
                />
              )}
              {shouldShowToxicity && (
                <StatCard 
                  title="Toxicity Stats" 
                  stats={stats.toxicity} 
                  total={tweets.length} 
                />
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsModal;