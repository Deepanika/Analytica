import { useParams } from 'react-router-dom';
import { AnalysisForm } from '../components/AnalysisForm';
import { BackgroundTweets } from '../components/BackgroundTweets';
import { ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';

const backgrounds = {
  combined: 'from-gray-900 to-black',
  emotional: 'from-gray-900 to-black',
  toxicity: 'from-gray-900 to-black',
  sentimental: 'from-gray-900 to-black'
};

export const Analysis = () => {
  const { type = 'combined' } = useParams<{ type: 'combined' | 'emotional' | 'toxicity' | 'sentimental' }>();

  const handleAnalysis = async (data: { query: string; tweetCount: number }) => {
    try {
      // TODO: Implement API call to backend
      console.log('Analyzing:', { type, ...data });
    } catch (error) {
      console.error('Analysis failed:', error);
    }
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
      </div>
    </div>
  );
};
