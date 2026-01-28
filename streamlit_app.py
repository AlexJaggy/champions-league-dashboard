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
# CSS FÜR S24 ULTRA - OPTIMIERT
# ============================================================================
def load_custom_css():
    st.markdown("""
    <style>
    /* App-Container ohne Padding oben */
    .stApp { 
        max-width: 100%; 
        padding: 0rem !important; 
        background-color: #0e1117;
        margin-top: -80px !important;
    }
    
    /* Entfernt Streamlit Header Spacing */
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
    }
    
    /* Spalten-Layout: Links 33%, Rechts 67% */
    [data-testid="column"]:first-child {
        width: 33% !important;
        flex: 0 0 33% !important;
        min-width: 33% !important;
    }
    
    [data-testid="column"]:last-child {
        width: 67% !important;
        flex: 0 0 67% !important;
        min-width: 67% !important;
    }
    
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 4px !important;
    }

    /* Match Cards mit Team-Logos */
    .match-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 8px;
        padding: 8px;
        margin-bottom: 6px;
        text-align: center;
        border-left: 3px solid #3b82f6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .team-row {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        margin: 3px 0;
    }
    
    .team-logo {
        width: 20px;
        height: 20px;
        object-fit: contain;
    }
    
    .team-name { 
        font-size: 10px; 
        color: white; 
        white-space: nowrap; 
        overflow: hidden; 
        text-overflow: ellipsis;
        flex: 1;
        text-align: left;
    }
    
    .score { 
        font-size: 16px; 
        font-weight: bold; 
        color: #fbbf24; 
        margin: 6px 0;
        text-shadow: 0 0 10px rgba(251, 191, 36, 0.5);
    }
    
    .match-time { 
        font-size: 10px; 
        color: #94a3b8; 
        background: #334155;
        padding: 3px 8px;
        border-radius: 4px;
        display: inline-block;
    }
    
    /* Tabellen-Styling */
    .standings-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 10px;
        color: white;
        background: #1e293b;
        border-radius: 8px;
        overflow: hidden;
    }
    
    .standings-table th {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        padding: 8px 4px;
        text-align: center;
        font-weight: bold;
        font-size: 10px;
        position: sticky;
        top: 0;
        z-index: 10;
    }
    
    .standings-table td {
        padding: 6px 4px;
        border-bottom: 1px solid #334155;
        text-align: center;
    }
    
    .standings-table tr:hover {
        background: #334155;
    }
    
    .pos-cell {
        color: #3b82f6;
        font-weight: bold;
        font-size: 11px;
    }
    
    .team-cell {
        text-align: left !important;
        padding-left: 8px !important;
    }
    
    .gd-positive {
        color: #10b981;
    }
    
    .gd-negative {
        color: #ef4444;
    }
    
    .gd-neutral {
        color: #94a3b8;
    }
    
    /* Header */
    h1 { 
        font-size: 16px !important; 
        margin: 8px 0 !important; 
        color: white;
        text-align: center;
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        padding: 8px;
        border-radius: 8px;
    }
    
    h2 { 
        font-size: 12px !important; 
        margin: 6px 0 !important; 
        color: #94a3b8;
        text-align: center;
    }
    
    /* Versteckt Streamlit Branding */
    #MainMenu, footer, header { visibility: hidden; }
    
    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0f172a;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #3b82f6;
        border-radius: 3px;
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# DATEN-FUNKTIONEN
# ============================================================================
def get_api_data(url):
    try:
        r = requests.get(url, headers={"X-Auth-Token": API_KEY}, timeout=10)
        return r.json() if r.status_code == 200 else None
    except: 
        return None

def display_matches(data):
    if not data or 'matches' not in data: 
        st.markdown('<div style="color: #94a3b8; text-align: center; padding: 20px;">Keine Spiele verfügbar</div>', unsafe_allow_html=True)
        return
    
    today = datetime.now().date()
    matches_shown = 0
    
    for m in data['matches']:
        # Korrektur der Zeitzone (UTC+1)
        utc_time = datetime.strptime(m['utcDate'], '%Y-%m-%dT%H:%M:%SZ')
        local_time = utc_time + timedelta(hours=1)
        
        if local_time.date() == today or m['status'] == 'IN_PLAY':
            home_name = m['homeTeam']['shortName'] or m['homeTeam']['name'][:12]
            away_name = m['awayTeam']['shortName'] or m['awayTeam']['name'][:12]
            home_logo = m['homeTeam'].get('crest', '')
            away_logo = m['awayTeam'].get('crest', '')
            
            # Live-Spiel oder geplantes Spiel
            if m['status'] == 'IN_PLAY':
                score_html = f'<div class="score">{m["score"]["fullTime"]["home"]} : {m["score"]["fullTime"]["away"]}</div>'
            else:
                score_html = f'<div class="match-time">⏰ {local_time.strftime("%H:%M")}</div>'
            
            # Team-Zeilen mit Logos
            home_html = f'<div class="team-row"><img src="{home_logo}" class="team-logo" onerror="this.style.display=\'none\'"><div class="team-name">{home_name}</div></div>'
            away_html = f'<div class="team-row"><img src="{away_logo}" class="team-logo" onerror="this.style.display=\'none\'"><div class="team-name">{away_name}</div></div>'
            
            st.markdown(f'''
            <div class="match-card">
                {home_html}
                {score_html}
                {away_html}
            </div>
            ''', unsafe_allow_html=True)
            
            matches_shown += 1
    
    if matches_shown == 0:
        st.markdown('<div style="color: #94a3b8; text-align: center; padding: 20px;">Heute keine Spiele</div>', unsafe_allow_html=True)

def display_standings(data):
    if not data or 'standings' not in data: 
        st.markdown('<div style="color: #94a3b8; text-align: center; padding: 20px;">Tabelle nicht verfügbar</div>', unsafe_allow_html=True)
        return
    
    table = data['standings'][0]['table']
    
    # HTML-Tabelle mit Tordifferenz
    html = '<table class="standings-table">'
    html += '''
    <thead>
        <tr>
            <th>#</th>
            <th style="text-align:left; padding-left:8px;">Team</th>
            <th>TD</th>
            <th>P</th>
        </tr>
    </thead>
    <tbody>
    '''
    
    for e in table:
        name = e['team']['shortName'] or e['team']['name']
        name = (name[:10] + '..') if len(name) > 11 else name
        
        # Tordifferenz berechnen und einfärben
        goal_diff = e['goalsFor'] - e['goalsAgainst']
        if goal_diff > 0:
            gd_class = "gd-positive"
            gd_text = f"+{goal_diff}"
        elif goal_diff < 0:
            gd_class = "gd-negative"
            gd_text = str(goal_diff)
        else:
            gd_class = "gd-neutral"
            gd_text = "0"
        
        html += f'''
        <tr>
            <td class="pos-cell">{e["position"]}</td>
            <td class="team-cell">{name}</td>
            <td class="{gd_class}">{gd_text}</td>
            <td style="font-weight:bold; color:#fbbf24;">{e["points"]}</td>
        </tr>
        '''
    
    html += '</tbody></table>'
    st.markdown(html, unsafe_allow_html=True)

# ============================================================================
# MAIN APP
# ============================================================================
def main():
    st.set_page_config(
        page_title="⚽ CL Live",
        page_icon="⚽",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    load_custom_css()
    
    # Kompakter Header
    st.markdown("# ⚽ Champions League LIVE")
    
    # Daten laden
    m_data = get_api_data(MATCHES_URL)
    s_data = get_api_data(STANDINGS_URL)
    
    # Spalten: Links 33%, Rechts 67%
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("## 🏁 Heute")
        display_matches(m_data)
        
    with col2:
        st.markdown("## 📊 Tabelle")
        display_standings(s_data)

    # Auto-Refresh
    time.sleep(30)
    st.rerun()

if __name__ == "__main__":
    main()
