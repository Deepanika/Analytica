# Analytica

## 📌 Overview
Analytica is a web-based application for real-time Twitter sentiment analysis, toxicity detection, and emotion recognition. It provides insights into public opinion by leveraging NLP models to analyze tweets.

## 🚀 Features
- **Sentiment Analysis**: Classifies tweets as Positive, Negative, or Neutral.
- **Toxicity Detection**: Identifies harmful or offensive content in tweets.
- **Emotion Recognition**: Detects emotions such as joy, sadness, anger, and optimism.
- **Live Tweet Wall**: Displays real-time tweets with sentiment and emotion analysis.
- **User Authentication**: Allows users to register, log in, and track their history.
- **Leaderboard**: Highlights top users based on interactions and analytics.

## 📂 Project Structure
```
deepanika-analytica/
├── docker-compose.yml  # Docker configuration
├── requirement.txt  # Dependencies
├── Backend/
│   ├── manage.py  # Django project manager
│   ├── Analytica/  # Django project settings
│   ├── models/  # Jupyter notebooks for ML models
│   ├── templates/  # HTML templates for frontend
│   ├── twitter_app/  # Django app handling Twitter analysis
│   └── db.sqlite3  # Database (SQLite for development)
└── Frontend/
    ├── src/
    │   ├── components/  # React components
    │   ├── pages/  # Page-based structure
    │   ├── utils/  # Utility functions
    ├── package.json  # Dependencies
    ├── tailwind.config.js  # Styling configuration
    └── vite.config.ts  # Frontend configuration
```

## 🛠️ Installation
### Prerequisites
- Python 3.8+
- Node.js & npm
- Docker (optional, for containerized setup)

### Backend Setup
```sh
cd Backend
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirement.txt
python manage.py migrate
python manage.py runserver
```

### Frontend Setup
```sh
cd Frontend
npm install
npm run dev
```

### Running with Docker
```sh
docker-compose up --build
```

## 🔗 API Endpoints
### Twitter Analysis API
- **`POST /api/tweet/scrape/`** - Fetch tweets and analyze them
- **`GET /api/livewall/getTweets/`** - Retrieve real-time analyzed tweets
- **`GET /api/history/tweets/{id}/`** - Fetch previous analysis history

## 📸 Screenshots
![Home Page](https://via.placeholder.com/600x300?text=Home+Page)
![Analysis Results](https://via.placeholder.com/600x300?text=Analysis+Results)

## 🎯 Future Enhancements
- Deploy using AWS or Heroku
- Add multilingual sentiment analysis
- Integrate a user dashboard for analytics

## ✨ Contributors
- **Aditya Srivastava** (Lead Developer)
- **Deepanika Gupta** (Lead Developer)
- **Kartik Saini** (Lead Developer)

## 📜 License
This project is licensed under the MIT License.

