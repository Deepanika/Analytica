import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Home } from './pages/Home';
import { Login } from './pages/Login';
import { SignUp } from './pages/SignUp';
import { Analysis } from './pages/Analysis';
import { Leaderboard } from './pages/Leaderboard';
import { History } from './pages/History';
import LiveWall from './pages/LiveWall';
import { useEffect } from 'react';

function App() {

  useEffect(() => {
    fetch('http://localhost:8000/api/auth/csrf/', { credentials: 'include' }); // ✅ Set CSRF cookie for session
  }, []);
  
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="/analysis/:type" element={<Analysis />} />
        <Route path="/leaderboard" element={<Leaderboard />} />
        <Route path="/history" element={<History />} />
        <Route path="/livewall" element={<LiveWall />} />
      </Routes>
    </Router>
  );
}

export default App;