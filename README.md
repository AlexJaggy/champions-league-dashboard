# ⚽ Champions League Live Dashboard

A mobile-optimized live dashboard for Champions League matches, built with Python and Streamlit. Shows today's matches with live scores, goals, cards, substitutions, and the current league table.

## What it does

- **Live scores** – auto-refreshes every 30 seconds
- **Match details** – goals, yellow/red cards, substitutions per game
- **League table** – current standings with goal difference and points
- **Mobile-first layout** – optimized for Samsung S24 Ultra (33/67 split, no-wrap columns)

## Tech stack

- [Streamlit](https://streamlit.io)
- [football-data.org API](https://www.football-data.org) (free tier)
- Python 3

## Setup

**1. Get a free API key**

Register at [football-data.org](https://www.football-data.org/client/register) – free tier covers Champions League data.

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Set your API key as environment variable**

```bash
export FOOTBALL_API_KEY=your_key_here
```

**4. Run the app**

```bash
streamlit run streamlit_app.py
```

## Requirements

```
streamlit==1.31.0
requests==2.31.0
```

## Notes

- Times are displayed in CET (UTC+1)
- API key must be set as environment variable – never hardcode it
