# PolyPulse 🌍💓

**Real-time global sentiment monitor powered by Polymarket's real-money prediction markets.**

PolyPulse turns crowd-sourced trading activity on Polymarket into a live pulse of worldwide sentiment — politics, crypto, macro, geopolitics, sports, culture, and breaking news.

When probabilities shift fast with volume spikes, **PolyPulse sees it before Twitter polls or headlines do.**

Real money ≠ fake likes.  
→ Wisdom of the crowd, skin in the game.

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)](https://www.python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-Deploy-blue?logo=streamlit)](https://streamlit.io)
[![Polymarket](https://img.shields.io/badge/Data-Polymarket-orange)](https://docs.polymarket.com)

## Why PolyPulse?

Polymarket prices = market-implied probabilities backed by actual USDC trades.  
- Sudden 7% jump on "Will X happen?" + 3× volume = **real sentiment shift**  
- Open interest surges = conviction building  
- Large whale orders or book depth changes = early conviction signals  

PolyPulse aggregates this into clean indices, movers, heatmaps, and alerts — the decentralized alternative to traditional sentiment trackers.

## Features (Current MVP)

- 🔍 Discover & filter **active markets** by tags, volume, liquidity (Gamma API)
- 📈 Real-time **prices/probabilities**, midpoints, last trades (CLOB API)
- 📊 Volume, open interest, recent trades history (Data API)
- ⚡ Basic **sentiment scoring** (price delta × volume, momentum signals)
- 🖥️ Live **Streamlit dashboard**: top movers, category indices, price charts, volume heatmaps
- 🔄 Background polling for near-real-time updates

## Roadmap (What's Next)

- [ ] WebSocket streaming from CLOB for sub-second price updates
- [ ] Persistent time-series DB (SQLite → PostgreSQL/TimescaleDB)
- [ ] Advanced sentiment indices (by region, topic, macro themes)
- [ ] Anomaly detection & alerts (Telegram, Discord, email)
- [ ] Historical backtesting vs real-world outcomes
- [ ] Topic clustering / NLP on market questions
- [ ] Export API / public JSON feeds
- [ ] Dark mode + mobile-friendly dashboard

## Tech Stack

- **Language**: Python 3.11+
- **API Clients**: `requests` + official `py-clob-client`
- **Dashboard**: Streamlit (fast prototyping → production)
- **Scheduling**: APScheduler (polling)
- **Data**: Pandas + Plotly (viz) → SQLite (storage)
- **Future**: FastAPI backend, Celery, Redis, WebSockets

## 🚀 AI Agents (NEW — PolyPulse Intelligence Layer)

PolyPulse now runs **autonomous AI agents** powered by CrewAI + your favorite LLM.

### What the agents do
- Real-time sentiment analysis
- Anomaly detection with explanations
- Daily narrative reports
- Category-specific guardians (Politics, Crypto, Macro…)

### How to enable AI
```bash
# Add to .env
LLM_API_KEY=sk-...
LLM_PROVIDER=openai   # or groq, anthropic, xai

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/PolyPulse.git
cd PolyPulse

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Create .env from example if needed later
cp .env.example .env

# 4. Launch the dashboard
streamlit run src/dashboard.py


### Next Steps (Pick One)
1. **Fastest** — I’ll give you the full `agents/` folder + updated `requirements.txt` and `dashboard.py` right now (just say “drop the full code”).
2. **Smarter** — Use **xAI’s Grok API** (truth-seeking + fun) instead of OpenAI — I can show you the exact config.
3. **Viral mode** — Add a public “Live AI Pulse” page that tweets the top insight every hour (I’ll code the Twitter bot part too).

This single addition makes PolyPulse feel like a $10M startup tool instead of a side project.

Want me to **drop the complete ready-to-copy code** for the agents right now? Or first decide on the LLM provider (OpenAI, Groq, xAI, etc.)?  

Just say the word and we ship the AI layer today. 🔥
