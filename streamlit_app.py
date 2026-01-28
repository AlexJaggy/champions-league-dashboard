import streamlit as st
import requests
import time
import os
from datetime import datetime, timedelta

# ============================================================================
# KONFIGURATION
# ============================================================================
API_KEY = os.environ.get("FOOTBALL_API_KEY") or "c1714469c0374ef4819fc9375a27269f"
MATCHES_URL = "https://api.football-data.org/v4/competitions/CL/matches"
STANDINGS_URL = "https://api.football-data.org/v4/competitions/CL/standings"

# ============================================================================
# CSS FÜR S24 ULTRA (ERZWINGT SIDE-BY-SIDE & FIXES HTML)
# ============================================================================
def load_custom_css():
    st.markdown("""
    <style>
    .stApp { max-width: 100%; padding: 0.1rem; background-color: #0e1117; }
    
    /* Erzwingt nebeneinander Darstellung auf mobilen Browsern */
    [data-testid="column"] {
        width: 50% !important;
        flex: 1 1 50% !important;
        min-width: 50% !important;
    }
    
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
    }

    .match-card {
        background: #1e293b;
        border-radius: 6px;
        padding: 6px;
        margin-bottom: 4px;
        text-align: center;
        border-left: 2px solid #3b82f6;
    }
    
    .team-name { font-size: 10px; color: white; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .score { font-size: 14px; font-weight: bold; color: #fbbf24; }
    .match-time { font-size: 9px; color: #94a3b8; }
    
    h1, h2 { font-size: 14px !important; margin: 5px 0 !important; color: white; }
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# DATEN-FUNKTIONEN
# ============================================================================
def get_api_data(url):
    try:
        r = requests.get(url, headers={"X-Auth-Token": API_KEY}, timeout=10)
        return r.json() if r.status_code == 200 else None
    except: return None

def display_matches(data):
    if not data or 'matches' not in data: return
    today = datetime.now().date()
    for m in data['matches']:
        # Korrektur der Zeitzone (UTC+1)
        utc_time = datetime.strptime(m['utcDate'], '%Y-%m-%dT%H:%M:%SZ')
        local_time = utc_time + timedelta(hours=1)
        
        if local_time.date() == today or m['status'] == 'IN_PLAY':
            home = m['homeTeam']['shortName'] or m['homeTeam']['name'][:10]
            away = m['awayTeam']['shortName'] or m['awayTeam']['name'][:10]
            
            content = f'<div class="score">{m["score"]["fullTime"]["home"]}:{m["score"]["fullTime"]["away"]}</div>' if m['status'] == 'IN_PLAY' else f'<div class="match-time">⏰ {local_time.strftime("%H:%M")}</div>'
            
            st.markdown(f'<div class="match-card"><div class="team-name">{home}</div>{content}<div class="team-name">{away}</div></div>', unsafe_allow_html=True)

def display_standings(data):
    if not data or 'standings' not in data: return
    table = data['standings'][0]['table']
    
    # Komplette HTML-Tabelle als EIN String
    html = '<table style="width:100%; border-collapse:collapse; font-size:9px; color:white;">'
    html += '<tr style="border-bottom:1px solid #334155;"><th>#</th><th style="text-align:left;">Team</th><th>P</th></tr>'
    
    for e in table:
        name = e['team']['shortName'] or e['team']['name']
        name = (name[:8] + '..') if len(name) > 9 else name
        html += f'<tr style="border-bottom:1px solid #1e293b;"><td style="color:#3b82f6;">{e["position"]}</td><td>{name}</td><td style="text-align:center;">{e["points"]}</td></tr>'
    
    html += '</table>'
    # Dieser Aufruf rendert das HTML korrekt
    st.markdown(html, unsafe_allow_html=True)

# ============================================================================
# MAIN APP
# ============================================================================
def main():
    st.set_page_config(page_title="CL", layout="wide")
    load_custom_css()
    
    st.markdown("## ⚽ CL LIVE (UTC+1)")
    
    m_data = get_api_data(MATCHES_URL)
    s_data = get_api_data(STANDINGS_URL)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("## 🏁 Spiele")
        display_matches(m_data)
        
    with col2:
        st.markdown("## 📊 Tabelle")
        display_standings(s_data)

    time.sleep(30)
    st.rerun()

if __name__ == "__main__":
    main()
    
