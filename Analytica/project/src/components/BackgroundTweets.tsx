import { motion } from 'framer-motion';
import { User, MessageCircle, Heart, Repeat2 } from 'lucide-react';

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
  }
];

const tweets = Array(15).fill(null).map(() => 
  sampleTweets[Math.floor(Math.random() * sampleTweets.length)]
);

export const BackgroundTweets = () => {
  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none">
      {tweets.map((tweet, i) => (
        <motion.div
          key={i}
          className="absolute w-64 bg-white/5 backdrop-blur-lg rounded-xl p-4 border border-white/10"
          initial={{
            opacity: 0,
            x: Math.random() * window.innerWidth,
            y: window.innerHeight + 100,
            rotate: -5 + Math.random() * 10
          }}
          animate={{
            opacity: [0, 0.7, 0],
            x: Math.random() * window.innerWidth,
            y: -200,
            rotate: -5 + Math.random() * 10
          }}
          transition={{
            duration: Math.random() * 20 + 15,
            repeat: Infinity,
            delay: Math.random() * 20
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