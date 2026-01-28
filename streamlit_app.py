import streamlit as st
import requests
import time
import os
from datetime import datetime, timedelta

# ============================================================================
# KONFIGURATION
# ============================================================================
API_KEY = os.environ.get("FOOTBALL_API_KEY")
if not API_KEY:
    try:
        API_KEY = st.secrets["FOOTBALL_API_KEY"]
    except (FileNotFoundError, KeyError):
        API_KEY = "c1714469c0374ef4819fc9375a27269f"

NTFY_TOPIC = "champions-league-goals"

# API Endpoints
MATCHES_URL = "https://api.football-data.org/v4/competitions/CL/matches"
STANDINGS_URL = "https://api.football-data.org/v4/competitions/CL/standings"

# ============================================================================
# CUSTOM CSS FÜR S24 ULTRA (NEBENEINANDER ERZWINGEN)
# ============================================================================
def load_custom_css():
    st.markdown("""
    <style>
    /* Hauptcontainer für Handy optimieren */
    .stApp { max-width: 100%; padding: 0.2rem; }
    
    /* Erzwingt nebeneinander Darstellung auch auf schmalen Bildschirmen */
    [data-testid="column"] {
        width: 49% !important;
        flex: 1 1 49% !important;
        min-width: 49% !important;
    }
    
    div[data-testid="stHorizontalBlock"] {
        display: flex;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 5px;
    }

    /* Match Cards kompakter */
    .match-card {
        background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
        border-radius: 8px;
        padding: 8px;
        margin-bottom: 6px;
        color: white;
        text-align: center;
        border-left: 3px solid #667eea;
    }
    
    .team-name { font-size: 11px; font-weight: bold; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .score { font-size: 18px; font-weight: bold; margin: 2px 0; color: #fbbf24; }
    .match-time { font-size: 10px; color: #a0aec0; }
    
    h1 { font-size: 18px !important; }
    h2 { font-size: 14px !important; margin-bottom: 10px !important; }

    /* UI Elemente verstecken */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# FUNKTIONEN
# ============================================================================

def get_api_data(url):
    headers = {"X-Auth-Token": API_KEY}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return response.json() if response.status_code == 200 else None
    except:
        return None

def display_matches(matches_data):
    if not matches_data or 'matches' not in matches_data:
        st.write("Keine Daten")
        return
    
    matches = matches_data['matches']
    today = datetime.now().date()
    
    found = False
    for match in matches:
        # Zeitzone: UTC + 1 Stunde (Anpassung für Deutschland/Winterzeit)
        match_time_utc = datetime.strptime(match['utcDate'], '%Y-%m-%dT%H:%M:%SZ')
        match_time_local = match_time_utc + timedelta(hours=1) # Hier +1 Std Anpassung
        
        if match_time_local.date() == today or match['status'] == 'IN_PLAY':
            found = True
            home = match['homeTeam']['shortName'] or match['homeTeam']['name']
            away = match['awayTeam']['shortName'] or match['awayTeam']['name']
            
            status_html = ""
            if match['status'] == 'IN_PLAY':
                score = match['score']['fullTime']
                status_html = f'<div class="score">{score["home"]}:{score["away"]}</div>'
            else:
                status_html = f'<div class="match-time">⏰ {match_time_local.strftime("%H:%M")}</div>'

            st.markdown(f"""
            <div class="match-card">
                <div class="team-name">{home}</div>
                {status_html}
                <div class="team-name">{away}</div>
            </div>
            """, unsafe_allow_html=True)
    
    if not found: st.info("Keine Spiele heute")

def display_standings(standings_data):
    if not standings_data or 'standings' not in standings_data: return
    table = standings_data['standings'][0]['table']
    
    html = """
    <table style="width:100%; border-collapse:collapse; font-size:10px; color:white;">
        <tr style="border-bottom: 1px solid #4a5568;">
            <th>#</th><th>Team</th><th>P</th>
        </tr>
    """
    for entry in table:
        name = entry['team']['shortName'] or entry['team']['name']
        if len(name) > 10: name = name[:9] + "."
        html += f"""
        <tr style="border-bottom: 1px solid #2d3748;">
            <td style="color:#667eea; font-weight:bold;">{entry['position']}</td>
            <td>{name}</td>
            <td style="text-align:center;">{entry['points']}</td>
        </tr>
        """
    html += "</table>"
    st.markdown(html, unsafe_allow_html=True)

# ============================================================================
# MAIN
# ============================================================================
def main():
    st.set_page_config(page_title="CL Live", layout="wide")
    load_custom_css()
    
    st.markdown("# ⚽ CL LIVE")
    
    col1, col2 = st.columns(2)
    
    matches_data = get_api_data(MATCHES_URL)
    standings_data = get_api_data(STANDINGS_URL)
    
    with col1:
        st.markdown("## 🏁 Spiele")
        display_matches(matches_data)
        
    with col2:
        st.markdown("## 📊 Tabelle")
        display_standings(standings_data)

    time.sleep(30)
    st.rerun()

if __name__ == "__main__":
    main()
