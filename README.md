# PulseRadar 🌍📡

**AI Predictive Sentiment Radar** — Real-money conviction from Polymarket + Kalshi + live social/news intelligence = forecasts of how prediction markets will actually move.

PulseRadar is the only open-source tool that doesn’t just show current odds — it actively scans X (Twitter), news headlines, and public data in real time, then deploys autonomous CrewAI agents to **predict** sentiment shifts and probability moves before they happen on both Polymarket and Kalshi.

Polls lie. Social media is noisy. Prediction markets show real money. PulseRadar shows what happens next.

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)](https://www.python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-Deploy-blue?logo=streamlit)](https://streamlit.io)

## ✨ What Makes PulseRadar Unique

- **Unified Live Pulse** — Real-time probabilities, volume spikes, and whale moves from **Polymarket + Kalshi**
- **Multi-Source Radar** — Scans X posts, news headlines, and web in real time
- **Predictive Oracle Agents** — CrewAI agents that correlate external signals with live market data and forecast “+12% odds move expected in 6h”
- **Global Sentiment Indices** — Politics, Crypto, Macro, Geopolitics, Culture across both platforms
- **Anomaly Detection + Alerts** — Catches divergences before the crowd

## Features

- 🔍 Combined market discovery from Polymarket & Kalshi
- 📈 Real-time prices, volume, open interest
- 🧠 Autonomous AI agents with external signal scanning
- 📊 Category sentiment indices & predictive reports
- 🤖 Natural-language chat: “Predict reaction to Fed rate cut news”

## Quick Start

```bash
git clone https://github.com/flamz321/PulseRadar.git
cd PulseRadar
pip install -r requirements.txt
cp .env.example .env
streamlit run src/dashboard.py
