# streaming--app
financial research
# Financial Streaming Agent Dashboard

A real-time financial analysis platform powered by Google's Agent Development Kit (ADK) and Gemini models. This application provides portfolio managers with comprehensive morning briefs, market data, and stock analysis through a streaming WebSocket interface.

## Features

- 🔴 **Real-time Streaming Responses** - WebSocket-based bidirectional communication
- 📊 **Comprehensive Market Data** - World indices, commodities, market movers
- 📈 **Stock Analysis** - Detailed financial metrics and company data
- 🌍 **Global Market Coverage** - Americas, Europe, and Asia markets
- 🤖 **Multi-Agent Architecture** - Specialized agents for different financial domains

## Architecture

### Agent System

The application uses a hierarchical agent structure:

- **Root Agent (`finagent`)** - Orchestrates all sub-agents and compiles responses
- **Market Brief Agent** - Generates market tone and key developments
- **World Indices Agent** - Fetches global market indices data
- **Commodities Agent** - Retrieves commodity prices (Gold, Silver, Copper, Oil, Gas)
- **Market Movers Agent** - Top 100 large-cap stock movers from TradingView


### Technology Stack

**Backend:**
- Python 3.8+
- FastAPI - Web framework
- Google ADK - Agent orchestration
- Google Gemini - AI models
- WebSockets - Real-time communication

**Frontend:**
- HTML5
- Vanilla JavaScript
- TailwindCSS - Styling

**Data Sources:**
- Yahoo Finance API (yfinance)
- TradingView (web scraping)
- Polygon.io (Treasury yields)
- Google Search (via ADK)

## Project Structure

```
streaming_app/
├── main.py                    # FastAPI server with WebSocket endpoints
├── .env                       # Environment variables (API keys)
├── requirements.txt           # Python dependencies
├── static/
│   ├── index.html            # Web interface
│   └── js/
│       └── app.js            # WebSocket client
└── finagent/                 # Agent package
    ├── __init__.py
    ├── agent.py              # Agent definitions
    ├── yahoo_stock_price.py  # Stock data fetcher
    ├── tv_market_movers_scraper.py  # TradingView scraper
    ├── yahoo_comm.py         # Commodity data fetcher
    ├── yahoo_indices.py      # World indices scraper
    └── polygon_Treasury_yields.py   # Treasury yields API
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Google Cloud account or Google AI Studio API key
- pip package manager

### Setup Steps

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd streaming_app
```

2. **Create a virtual environment**
```bash
python -m venv .venv

# Activate on macOS/Linux:
source .venv/bin/activate

# Activate on Windows:
.venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create a `.env` file in the `streaming_app` directory:

**Option 1: Using Google AI Studio (Recommended for development)**
```env
GOOGLE_API_KEY=your_api_key_here
```

Get your API key from: https://aistudio.google.com/apikey

**Option 2: Using Google Cloud Vertex AI**
```env
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_CLOUD_LOCATION=us-central1
```

And authenticate:
```bash
gcloud auth application-default login
```

5. **Optional: Configure Polygon.io API key** (for Treasury yields)

Add to `.env`:
```env
POLYGON_API_KEY=your_polygon_api_key_here
```

Get a free API key from: https://polygon.io

## Running the Application

### Local Development

```bash
cd streaming_app
python main.py
```

The server will start on `http://localhost:8080`

Open your browser and navigate to: `http://localhost:8080`

### Google Cloud Shell

If running in Google Cloud Shell:

1. Start the server:
```bash
python main.py
```

2. Click the **Web Preview** button in Cloud Shell
3. Select **Preview on port 8080**

The application will open in a new tab with WebSocket support over HTTPS.



## License

[Your License Here]

## Acknowledgments

- Google Agent Development Kit (ADK) team
- Yahoo Finance for market data
- TradingView for market movers data
- Polygon.io for Treasury yields API

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check the [ADK documentation](https://google.github.io/adk-docs/)
- Review [Gemini API docs](https://ai.google.dev/docs)

---

**⚠️ Disclaimer:** This application is for educational and informational purposes only. Not financial advice. Always verify data from official sources before making investment decisions.
