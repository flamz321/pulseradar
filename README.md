# PulseRadar 🌍📡

**AI-Powered Predictive Sentiment Radar**  
Real-money conviction from **Polymarket** + **Kalshi** meets live internet-wide intelligence.

PulseRadar deploys autonomous **CrewAI Predictive Oracle Agents** that **scour the entire internet in real time** — X (Twitter), Facebook, TikTok, Instagram, major news headlines from every country, blogs, forums, and thousands of other public sources — to understand exactly how the world is reacting to breaking events.

These agents then correlate that global reaction data with **actual skin-in-the-game trading activity** on Polymarket and Kalshi to detect patterns and **predict probability moves** before they appear in the markets.

Polls lie. Social media is noisy. Headlines are slow.  
PulseRadar shows you **what the world is actually feeling** — and **what the markets will do next**.

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)](https://www.python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-blue?logo=streamlit)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Built for crypto traders, prediction-market degens, macro analysts, and anyone who wants an edge from real-world sentiment patterns.**

### Why PulseRadar Is Different

Most tools only show you current odds.  
PulseRadar is the only open-source project that:

- **Scans the entire internet in real time** — X posts, Facebook discussions, TikTok & Instagram virality, global news wires, and every other public source
- **Builds live reaction patterns** — Detects sudden sentiment explosions the moment they happen anywhere online
- **Correlates with real money** — Matches those global reactions against live volume, whale flows, and probability shifts on **Polymarket** and **Kalshi**
- **Delivers predictive forecasts** — AI agents output clear predictions like “+12% odds move expected on Fed rate cut market in next 6–12 hours”

### ✨ Core Features

- **Unified Live Markets** — Polymarket + Kalshi in one clean dashboard
- **Global Sentiment Indices** — Real-time pulse scores across Politics, Crypto, Macro, Geopolitics, Culture
- **Predictive Oracle Agents** — Ask anything in plain English and get instant analysis + forecasts powered by **your choice of frontier model**
- **Internet-Wide Signal Scanning** — Continuously monitors X, Facebook, TikTok, Instagram, worldwide news, and public web sources
- **Anomaly & Pattern Detection** — Flags when online buzz is about to move real-money markets

### LLM Support – Works with Any Major Model

PulseRadar is **fully LLM-agnostic**. You can run the Predictive Oracle Agents with:

- **OpenAI** (gpt-4o, o1, etc.) – default
- **Anthropic Claude** (Claude 3.5 Sonnet / Opus) – best for deep reasoning
- **xAI Grok** – truth-seeking, uncensored, perfect for crypto
- **Groq** – blazing-fast inference (Llama 3.1, Mixtral)
- **Google Gemini** – strong multimodal & news understanding
- Any other model supported by LangChain

### Quick Start

```bash
git clone https://github.com/flamz321/PulseRadar.git
cd PulseRadar
pip install -r requirements.txt

# Optional extras for other LLMs
pip install langchain-anthropic langchain-xai langchain-groq langchain-google-genai
