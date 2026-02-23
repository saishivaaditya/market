# MarketMind — AI-Powered Sales & Marketing Intelligence

MarketMind is a powerful, glassmorphism-styled analytics platform that leverages **Groq LLaMA 3.3 70B** to generate high-performing marketing campaigns, craft personalized sales pitches, and qualify leads with advanced AI analysis.

![MarketMind Dashboard](file:///C:/Users/essad/.gemini/antigravity/brain/c1f2c45e-ed56-450b-84fc-00d5885eb434/analytics_dashboard.png)

## Features

- **AI Campaign Generator**: Tailored strategies for any audience and platform.
- **Sales Pitch Creator**: Persuasive pitches for specific customer personas.
- **Lead Qualifier**: Multi-dimensional scoring (Budget, Need, Urgency) with visual badges and conversion probability.
- **Advanced Analytics**: Interactive Chart.js graphs for sales trends, product performance, and sentiment analysis.
- **Modern UI**: Polished glassmorphism design with dark/light mode, smooth transitions, and responsive layout.
- **Secure Auth**: Google OAuth 2.0 integration.

## Tech Stack

- **Backend**: Python, Flask, Groq API (LLaMA 3.3 70B)
- **Frontend**: HTML5, Vanilla CSS (Glassmorphism), JavaScript (Chart.js)
- **Environment**: Managed via `.env` and `python-dotenv`

## Getting Started

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd marketmind
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**:
   Create a `.env` file in the root directory and add your Groq API Key:
   ```env
   GROQ_API_KEY=your_api_key_here
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```
   Open `http://localhost:5000` in your browser.

## Built with ❤️ by MarketMind Team
