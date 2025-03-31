import { motion } from 'framer-motion';
import { User, MessageCircle, Heart, Repeat2 } from 'lucide-react';
import { useEffect, useState } from 'react';

const sampleTweets = [
  {
    username: "TechEnthusiast",
    content: "Just discovered an amazing new framework! 🚀 #coding",
    likes: 234,
    retweets: 56
  },
  {
    username: "NaturePhotographer",
    content: "Captured this stunning sunset today! Nature never fails to amaze 🌅 #photography",
    likes: 789,
    retweets: 123
  },
  {
    username: "FoodieExplorer",
    content: "This homemade pasta was absolutely divine! 🍝 #foodie #cooking",
    likes: 456,
    retweets: 78
  },
  {
    username: "TravelBlogger",
    content: "Venice at dawn is pure magic ✨ #travel #wanderlust",
    likes: 1234,
    retweets: 345
  },
  {
    username: "MusicLover",
    content: "This new album is on repeat! 🎵 #music #nowplaying",
    likes: 567,
    retweets: 89
  },
  {
    username: "GamerZone",
    content: "Finally beat that insanely hard boss! 🎮🔥 #gaming #victory",
    likes: 678,
    retweets: 145
  },
  {
    username: "SpaceGeek",
    content: "The latest images from the James Webb Telescope are mind-blowing! 🪐✨ #astronomy #science",
    likes: 890,
    retweets: 312
  },
  {
    username: "FitnessFreak",
    content: "Morning workout done! Feeling pumped 💪 #fitness #healthylifestyle",
    likes: 432,
    retweets: 67
  },
  {
    username: "Bookworm",
    content: "Just finished an incredible novel! Highly recommend 📖 #reading #booklover",
    likes: 345,
    retweets: 92
  },
  {
    username: "CryptoTrader",
    content: "Bitcoin is on the rise again! 🚀📈 #crypto #investing",
    likes: 910,
    retweets: 278
  },
  {
    username: "MovieBuff",
    content: "That plot twist was INSANE! 🎬🤯 #movies #cinema",
    likes: 784,
    retweets: 134
  },
  {
    username: "PetLover",
    content: "My cat just did the funniest thing! 🐱😂 #pets #adorable",
    likes: 562,
    retweets: 104
  },
  {
    username: "Motivator",
    content: "Believe in yourself! You're capable of amazing things. 💙 #motivation #inspiration",
    likes: 1235,
    retweets: 410
  },
  {
    username: "Entrepreneur",
    content: "Success is built on consistency and patience. 💡 #business #hustle",
    likes: 678,
    retweets: 215
  },
  {
    username: "ScienceNerd",
    content: "Did you know? Water can boil and freeze at the same time under certain conditions! 🌡️ #science #funfact",
    likes: 523,
    retweets: 198
  },
  {
    username: "ComedyKing",
    content: "Why don’t skeletons fight each other? They don’t have the guts! 😂 #jokes #funny",
    likes: 432,
    retweets: 99
  },
  {
    username: "WeatherWatch",
    content: "Looks like a massive storm is coming in. Stay safe, everyone! ⛈️ #weatherupdate",
    likes: 743,
    retweets: 256
  },
  {
    username: "ArtisticSoul",
    content: "Finished my latest painting today! So proud of this one 🎨✨ #art #creative",
    likes: 654,
    retweets: 143
  },
  {
    username: "InvestorMindset",
    content: "Stock markets are unpredictable, but patience always pays off. 📈 #investing #finance",
    likes: 845,
    retweets: 234
  },
  {
    username: "HistoryBuff",
    content: "On this day in history, a major revolution began! 🏛️ #history #didyouknow",
    likes: 592,
    retweets: 176
  }
];


interface Tweet {
  username: string;
  content: string;
  likes: number;
  retweets: number;
  lane: number;
  speed: number;
  startDelay: number;
}

const TOTAL_LANES = 5; // Number of vertical lanes
const TWEETS_PER_LANE = 3; // Number of tweets per lane

export const BackgroundTweets = () => {
  const [tweets, setTweets] = useState<Tweet[]>([]);
  const [windowSize, setWindowSize] = useState({
    width: typeof window !== 'undefined' ? window.innerWidth : 1200,
    height: typeof window !== 'undefined' ? window.innerHeight : 800
  });

  useEffect(() => {
    const handleResize = () => {
      setWindowSize({
        width: window.innerWidth,
        height: window.innerHeight
      });
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    // Generate tweets with balanced distribution
    const newTweets: Tweet[] = [];
    
    for (let lane = 0; lane < TOTAL_LANES; lane++) {
      for (let i = 0; i < TWEETS_PER_LANE; i++) {
        const randomTweet = sampleTweets[Math.floor(Math.random() * sampleTweets.length)];
        newTweets.push({
          ...randomTweet,
          lane,
          speed: 20 + Math.random() * 10, // Random speed between 20-30 seconds
          startDelay: (lane * 4) + (i * 7) // Staggered delay based on lane and position
        });
      }
    }

    setTweets(newTweets);
  }, []);

  const getLaneX = (lane: number) => {
    const laneWidth = windowSize.width / TOTAL_LANES;
    const baseX = (lane * laneWidth) + (laneWidth / 2) - 128; // Center in lane (256px/2 = 128)
    const wiggleRoom = laneWidth * 0.2; // 20% of lane width for random offset
    return baseX + (Math.random() * wiggleRoom - wiggleRoom / 2);
  };

  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none">
      {tweets.map((tweet, i) => (
        <motion.div
          key={i}
          className="absolute w-64 bg-white/5 backdrop-blur-lg rounded-xl p-4 border border-white/10 shadow-lg"
          initial={{
            opacity: 0,
            x: getLaneX(tweet.lane),
            y: -100,
            rotate: -2 + Math.random() * 4
          }}
          animate={{
            opacity: [0, 0.7, 0],
            x: getLaneX(tweet.lane),
            y: windowSize.height + 100,
            rotate: -2 + Math.random() * 4
          }}
          transition={{
            duration: tweet.speed,
            repeat: Infinity,
            delay: tweet.startDelay,
            ease: "linear"
          }}
        >
          <div className="flex items-center gap-2 mb-2">
            <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center">
              <User className="w-4 h-4 text-white/60" />
            </div>
            <span className="text-white/80 font-medium">@{tweet.username}</span>
          </div>
          <p className="text-white/60 text-sm mb-3">{tweet.content}</p>
          <div className="flex items-center gap-4 text-white/40 text-xs">
            <div className="flex items-center gap-1">
              <Heart className="w-3 h-3" />
              <span>{tweet.likes}</span>
            </div>
            <div className="flex items-center gap-1">
              <Repeat2 className="w-3 h-3" />
              <span>{tweet.retweets}</span>
            </div>
            <div className="flex items-center gap-1">
              <MessageCircle className="w-3 h-3" />
              <span>{Math.floor(tweet.likes / 3)}</span>
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  );
};