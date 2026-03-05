# 🚀 ML-Driven Cryptocurrency Price Forecasting Platform

A full-stack web application for cryptocurrency price forecasting using machine learning models (LSTM and Gradient Boosting). Features real-time market data, technical indicators, transparent model metrics, and an elegant user interface.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![React](https://img.shields.io/badge/React-18+-61DAFB.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-FF6F00.svg)

## ✨ Features

### 📈 Price Forecasting
- **Hourly Forecasting**: LSTM-based 24-hour predictions with hourly granularity
- **Daily Forecasting**: Gradient Boosting models for 7, 15, and 30-day horizons
- **Multiple Cryptocurrencies**: BTC, ETH, BNB, SOL, XRP, ADA, DOGE, DOT, MATIC, LTC

### 📊 Technical Analysis
- Real-time price data via Binance WebSocket
- Technical indicators: SMA, EMA, Bollinger Bands, RSI
- Interactive charts with historical and forecasted data
- Multi-currency support (USD, EUR, GBP, INR, etc.)

### 🔍 Model Transparency
- Training & testing metrics (RMSE, MAE, R²)
- Per-horizon performance visualization
- Feature importance analysis via Mutual Information
- Model architecture details

### 👤 User Features
- Secure authentication (JWT-based)
- Forecast history tracking
- User profiles with customization
- Responsive, modern UI with glassmorphism design

## 🏗️ Project Structure

```

WebApplication/
├── client/                 # React + Vite frontend
│   ├── src/
│   ├── components/     # Reusable UI components
│   │   ├── pages/          # Page components
│   │   ├── hooks/          # Custom React hooks
│   │   ├── services/       # API service layer
│   │   └── constants/      # Configuration constants
│   └── package.json
│  
├── server/                 # FastAPI backend
│   ├── app/
│   │   ├── routers/        # API route handlers
│   │   ├── services/       # Business logic
│   │   ├── models.py       # Pydantic models
│   │   └── config.py       # Configuration
│   └── requirements.txt
│   
├── Models_Hourly/          # LSTM models for hourly forecasting
├── Models_Daily_ML/        # Gradient Boosting models for daily forecasting
├── Scalers_Hourly/         # Feature scalers for hourly models
├── Scalers_Daily_ML/       # Feature scalers for daily models
└── Metadata/               # Training metadata JSON files



## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- MongoDB (optional, for user features)

### Backend Setup

1. **Navigate to server directory:**
   ```bash
   cd WebApplication/server
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   Create a `.env` file based on `.env.example`:
   ```env
   MONGODB_URI=mongodb://localhost:27017
   MONGODB_DB=crypto_forecast
   JWT_SECRET=your-secret-key-here
   CORS_ORIGINS=http://localhost:5173
   ```

5. **Run the API server:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

### Frontend Setup

1. **Navigate to client directory:**
   ```bash
   cd WebApplication/client
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure API base (optional):**
   Create `.env` file:
   ```env
   VITE_API_BASE=http://localhost:8000
   ```

4. **Start development server:**
   ```bash
   npm run dev
   ```

5. **Open browser:**
   Navigate to `http://localhost:5173`

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/signup` | Create new user account |
| POST | `/auth/login` | Login and get access token |
| POST | `/auth/logout` | Logout and revoke session |
| GET | `/auth/me` | Get current user info |

### Forecasting
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/forecast` | Generate daily forecast |
| POST | `/forecast/hourly` | Generate 24-hour forecast |
| GET | `/forecast/history` | Get user's forecast history |
| GET | `/forecast/coins` | List available coins |

### Dashboard & Training
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dashboard/metadata` | Get training metrics for all coins |
| GET | `/coin/{coin}/training/metadata` | Get detailed training metadata |
| GET | `/coin/{coin}/training/metadata/{coin}` | Get coin-specific metadata |

### User Profile
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/profile` | Get user profile |
| POST | `/profile` | Update user profile |
| POST | `/profile/photo` | Upload profile photo |

### News Section 

The application offers a dedicated news page where users can read the latest cryptocurrency headlines, filter by coin, and dive deeper with AI‑powered analysis.  Highlights include:

- **Aggregated Headlines** – pulls from free sources (CryptoCompare) and keeps the feed up‑to‑date.
- **Sentiment Scoring** – every article is run through a lightweight rule‑based analyzer so users can quickly see if the story is bullish, bearish or neutral.
- **Trending/Hot News** – the frontend can show the top stories based on recency and sentiment strength.
- **AI News Analyst** – click a headline to open a modal that uses Google Gemini to generate a summary, sentiment breakdown and price‑impact analysis.  Follow‑up questions are handled via a chat interface.

#### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/news` | Fetch recent news; optional query parameters `coin` (e.g. BTC, ETH) and `date_range` (`today` or `30d`). Returns sentiment for each item. |
| GET | `/news/trending` | Get top 10 trending/hot crypto stories ranked by recency & sentiment. |
| POST | `/news/summarize` | Send article title/body to Gemini and receive a structured AI summary with sentiment & price‑impact analysis. |
| POST | `/news/chat` | Multi‑turn chat endpoint for follow‑up questions about a specific article. |



## 🤖 Model Architecture

### Hourly LSTM Model (24-hour forecast)
- **Architecture**: 2-layer LSTM (128 → 64 units) with dropout
- **Features**: OHLCV + MA_12, MA_24, MA_168, Returns, Volatility, Price_Range, Price_Change
- **Output**: 24 hourly price predictions

### Daily Gradient Boosting Model (7/15/30-day forecast)
- **Algorithm**: Gradient Boosting Regressor
- **Parameters**: n_estimators=50, max_depth=5, learning_rate=0.05
- **Features**: Lag features, rolling statistics, technical indicators

## 🎨 UI Screenshots

The application features a modern, responsive design with:
- Dark theme with glassmorphism effects
- Smooth animations and transitions
- Interactive charts powered by Recharts
- Mobile-friendly layout

## 🛠️ Technologies Used

### Backend
- **FastAPI** - High-performance Python web framework
- **TensorFlow/Keras** - Deep learning for LSTM models
- **Scikit-learn** - Gradient Boosting and preprocessing
- **MongoDB** - User data and session storage
- **JWT** - Secure authentication

### Frontend
- **React 18** - UI library with hooks
- **Vite** - Fast build tool
- **TailwindCSS** - Utility-first CSS framework
- **Recharts** - Charting library
- **React Router** - Client-side routing

## 📝 Notes

- Access tokens expire after 12 hours; logout revokes active sessions
- Forecast routing: "Next 24h" uses hourly LSTM models; 7/15/30d use daily GB models
- Technical sentiment derived from RSI, MACD, EMA, and volatility analysis on predicted series
- Models are cached for instant predictions; use "Force Retrain" to regenerate


## 📄 License

This project is developed as part of the Infosys Springboard internship program.
