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
# CSS FÜR S24 ULTRA - NO-WRAP ERZWUNGEN
# ============================================================================
def load_custom_css():
    st.markdown("""
    <style>
    /* Basis */
    .stApp { 
        max-width: 100%; 
        padding: 0rem !important; 
        background-color: #0e1117;
    }
    
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        max-width: 100% !important;
    }
    
    /* NO-WRAP RULE - Zwingt Spalten nebeneinander */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 5px !important;
        overflow-x: auto !important;
    }
    
    /* Spalten: Links 33%, Rechts 67% */
    [data-testid="column"]:first-child {
        width: 33% !important;
        flex: 0 0 33% !important;
        min-width: 33% !important;
        max-width: 33% !important;
    }
    
    [data-testid="column"]:last-child {
        width: 67% !important;
        flex: 0 0 67% !important;
        min-width: 67% !important;
        max-width: 67% !important;
    }

    /* Match Cards mit Logos */
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
    
    /* Streamlit Dataframe Styling */
    [data-testid="stDataFrame"] {
        width: 100% !important;
    }
    
    .stDataFrame > div {
        width: 100% !important;
    }
    
    /* Streamlit Table Cells */
    [data-testid="stDataFrame"] td,
    [data-testid="stDataFrame"] th {
        font-size: 9px !important;
        padding: 4px 2px !important;
        text-align: center !important;
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
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
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

def get_match_details(match_id):
    """Lädt Details für ein einzelnes Spiel"""
    url = f"https://api.football-data.org/v4/matches/{match_id}"
    return get_api_data(url)

def display_match_details(match_id):
    """Zeigt Spielverlauf: Tore, Karten, Auswechslungen"""
    details = get_match_details(match_id)
    
    if not details:
        st.markdown('<div style="color: #ef4444; font-size: 9px;">⚠️ Details nicht verfügbar</div>', unsafe_allow_html=True)
        return
    
    # Tore
    goals = details.get('goals', [])
    if goals:
        st.markdown("**⚽ TORE:**")
        for g in goals:
            minute = g.get('minute', '?')
            scorer = g.get('scorer', {}).get('name', 'Unbekannt')
            team = g.get('team', {}).get('shortName') or g.get('team', {}).get('name', '')[:10]
            st.markdown(f"<div style='font-size: 9px; color: #10b981;'>{minute}' ⚽ {scorer} ({team})</div>", unsafe_allow_html=True)
    
    # Karten
    bookings = details.get('bookings', [])
    if bookings:
        st.markdown("**🟨 KARTEN:**")
        for b in bookings:
            minute = b.get('minute', '?')
            player = b.get('player', {}).get('name', 'Unbekannt')
            team = b.get('team', {}).get('shortName') or b.get('team', {}).get('name', '')[:10]
            card = b.get('card', 'YELLOW')
            icon = '🟥' if card == 'RED' else '🟨'
            color = '#ef4444' if card == 'RED' else '#fbbf24'
            st.markdown(f"<div style='font-size: 9px; color: {color};'>{minute}' {icon} {player} ({team})</div>", unsafe_allow_html=True)
    
    # Auswechslungen
    substitutions = details.get('substitutions', [])
    if substitutions:
        st.markdown("**🔄 WECHSEL:**")
        for s in substitutions:
            minute = s.get('minute', '?')
            player_out = s.get('playerOut', {}).get('name', 'Unbekannt')
            player_in = s.get('playerIn', {}).get('name', 'Unbekannt')
            team = s.get('team', {}).get('shortName') or s.get('team', {}).get('name', '')[:10]
            st.markdown(f"<div style='font-size: 9px; color: #94a3b8;'>{minute}' 🔄 {player_out} ➡️ {player_in} ({team})</div>", unsafe_allow_html=True)
    
    if not goals and not bookings and not substitutions:
        st.markdown('<div style="color: #94a3b8; font-size: 9px;">Noch keine Ereignisse</div>', unsafe_allow_html=True)

def display_matches(data):
    if not data or 'matches' not in data: 
        st.markdown('<div style="color: #94a3b8; text-align: center; padding: 20px;">Keine Daten</div>', unsafe_allow_html=True)
        return
    
    today = datetime.now().date()
    matches_shown = 0
    
    for m in data['matches']:
        # UTC+1 Korrektur
        utc_time = datetime.strptime(m['utcDate'], '%Y-%m-%dT%H:%M:%SZ')
        local_time = utc_time + timedelta(hours=1)
        
        if local_time.date() == today or m['status'] == 'IN_PLAY':
            home_name = m['homeTeam']['shortName'] or m['homeTeam']['name'][:12]
            away_name = m['awayTeam']['shortName'] or m['awayTeam']['name'][:12]
            match_id = m['id']
            
            if m['status'] == 'IN_PLAY':
                score = f"{m['score']['fullTime']['home']}:{m['score']['fullTime']['away']}"
                label = f"⚽ {home_name} {score} {away_name}"
            else:
                time_str = local_time.strftime("%H:%M")
                label = f"⏰ {time_str} | {home_name} vs {away_name}"
            
            # Expander mit Match-Details
            with st.expander(label, expanded=False):
                display_match_details(match_id)
            
            matches_shown += 1
    
    if matches_shown == 0:
        st.markdown('<div style="color: #94a3b8; text-align: center; padding: 20px;">Heute keine Spiele</div>', unsafe_allow_html=True)

def display_standings(data):
    if not data or 'standings' not in data: 
        st.markdown('<div style="color: #94a3b8; text-align: center; padding: 20px;">Keine Daten</div>', unsafe_allow_html=True)
        return
    
    table = data['standings'][0]['table']
    
    # Erstelle kompakte Tabellen-Zeilen ohne HTML
    for e in table:
        pos = e['position']
        name = e['team']['shortName'] or e['team']['name']
        name = name[:10] + '..' if len(name) > 11 else name
        
        gd = e['goalsFor'] - e['goalsAgainst']
        gd_text = f"+{gd}" if gd > 0 else str(gd)
        gd_color = "#10b981" if gd > 0 else ("#ef4444" if gd < 0 else "#94a3b8")
        
        pts = e['points']
        
        # Kompakte Zeile als HTML
        st.markdown(f'''
        <div style="
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 6px 8px;
            margin: 2px 0;
            background: #1e293b;
            border-radius: 6px;
            border-left: 3px solid #3b82f6;
        ">
            <span style="color: #3b82f6; font-weight: bold; font-size: 10px; width: 15%;">{pos}</span>
            <span style="color: white; font-size: 9px; text-align: left; flex: 1;">{name}</span>
            <span style="color: {gd_color}; font-size: 9px; width: 20%; text-align: center;">{gd_text}</span>
            <span style="color: #fbbf24; font-weight: bold; font-size: 10px; width: 15%; text-align: right;">{pts}</span>
        </div>
        ''', unsafe_allow_html=True)

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
    
    st.markdown("# ⚽ CL LIVE")
    
    m_data = get_api_data(MATCHES_URL)
    s_data = get_api_data(STANDINGS_URL)
    
    # Spalten: 33% und 67%
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("## 🏁 Heute")
        display_matches(m_data)
        
    with col2:
        st.markdown("## 📊 Tabelle")
        display_standings(s_data)

    time.sleep(30)
    st.rerun()

if __name__ == "__main__":
    main()
