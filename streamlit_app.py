import streamlit as st
import requests
import time
from datetime import datetime

# ============================================================================
# KONFIGURATION - Hier musst du später deinen API-Key eintragen!
# ============================================================================
API_KEY = st.secrets.get("FOOTBALL_API_KEY", "DEIN_API_KEY_HIER")
NTFY_TOPIC = "champions-league-goals"  # Du kannst das ändern!

# API Endpoints
MATCHES_URL = "https://api.football-data.org/v4/competitions/CL/matches"
STANDINGS_URL = "https://api.football-data.org/v4/competitions/CL/standings"

# ============================================================================
# CUSTOM CSS FÜR SAMSUNG GALAXY S24 ULTRA
# ============================================================================
def load_custom_css():
    st.markdown("""
    <style>
    /* Basis-Styling */
    .stApp {
        max-width: 100%;
        padding: 0.5rem;
    }
    
    /* Split-Screen Layout - WICHTIG: Verhindert Umbruch! */
    .split-container {
        display: flex;
        gap: 10px;
        overflow-x: auto;
        min-width: 100%;
    }
    
    .split-column {
        flex: 1;
        min-width: 48%;
        max-width: 50%;
    }
    
    /* Tabellen-Styling */
    .match-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .live-badge {
        background: #ff4444;
        color: white;
        padding: 3px 8px;
        border-radius: 5px;
        font-size: 11px;
        font-weight: bold;
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    
    .score {
        font-size: 24px;
        font-weight: bold;
        text-align: center;
    }
    
    .team-name {
        font-size: 14px;
        margin: 5px 0;
    }
    
    /* Tabelle */
    .standings-table {
        font-size: 12px;
        width: 100%;
    }
    
    /* Header */
    h1 {
        font-size: 20px !important;
        margin-bottom: 10px !important;
    }
    
    h2 {
        font-size: 16px !important;
        margin-top: 5px !important;
    }
    
    /* Streamlit Button verstecken */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# FUNKTIONEN MIT ERROR-HANDLING
# ============================================================================

def get_api_data(url, max_retries=3):
    """
    Holt Daten von der API mit automatischen Wiederholungen
    """
    headers = {"X-Auth-Token": API_KEY}
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                # Rate Limit erreicht
                st.warning("⏱️ Zu viele Anfragen. Warte 60 Sekunden...")
                time.sleep(60)
            else:
                st.error(f"API Fehler: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            st.warning(f"⏱️ Timeout - Versuch {attempt + 1}/{max_retries}")
            time.sleep(2)
        except requests.exceptions.ConnectionError:
            st.warning(f"📡 Keine Internetverbindung - Versuch {attempt + 1}/{max_retries}")
            time.sleep(5)
        except Exception as e:
            st.error(f"❌ Unerwarteter Fehler: {str(e)}")
            return None
    
    st.error("❌ Konnte keine Daten laden nach mehreren Versuchen")
    return None

def send_goal_notification(home_team, away_team, score):
    """
    Sendet Push-Benachrichtigung über ntfy.sh
    """
    try:
        message = f"⚽ TOR! {home_team} {score} {away_team}"
        requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=message.encode('utf-8'),
            headers={
                "Title": "Champions League LIVE",
                "Priority": "high",
                "Tags": "soccer"
            },
            timeout=5
        )
    except Exception as e:
        # Fehler bei Benachrichtigung nicht anzeigen, um Dashboard nicht zu stören
        pass

def check_for_goals(current_matches, previous_matches):
    """
    Vergleicht aktuelle Spielstände mit vorherigen und sendet Benachrichtigungen
    """
    if not previous_matches:
        return
    
    for current in current_matches:
        match_id = current['id']
        
        # Finde vorheriges Spiel
        previous = next((m for m in previous_matches if m['id'] == match_id), None)
        
        if previous and current['status'] == 'IN_PLAY':
            current_score = current['score']['fullTime']
            previous_score = previous['score']['fullTime']
            
            # Prüfe auf Tor-Änderung
            if (current_score['home'] != previous_score['home'] or 
                current_score['away'] != previous_score['away']):
                
                score_text = f"{current_score['home']}:{current_score['away']}"
                send_goal_notification(
                    current['homeTeam']['name'],
                    current['awayTeam']['name'],
                    score_text
                )

def display_matches(matches_data):
    """
    Zeigt Live-Spiele und anstehende Spiele an
    """
    if not matches_data or 'matches' not in matches_data:
        st.error("❌ Keine Spieldaten verfügbar")
        return []
    
    matches = matches_data['matches']
    
    # Filtere nur heutige und Live-Spiele
    today_matches = []
    live_matches = []
    
    for match in matches:
        status = match['status']
        if status == 'IN_PLAY':
            live_matches.append(match)
        elif status in ['TIMED', 'SCHEDULED']:
            match_date = datetime.strptime(match['utcDate'], '%Y-%m-%dT%H:%M:%SZ')
            if match_date.date() == datetime.now().date():
                today_matches.append(match)
    
    # Live-Spiele anzeigen
    if live_matches:
        st.markdown("### 🔴 LIVE JETZT")
        for match in live_matches:
            score = match['score']['fullTime']
            home_team = match['homeTeam']['name']
            away_team = match['awayTeam']['name']
            minute = match.get('minute', '?')
            
            st.markdown(f"""
            <div class="match-card">
                <span class="live-badge">LIVE {minute}'</span>
                <div class="team-name">{home_team}</div>
                <div class="score">{score['home']} : {score['away']}</div>
                <div class="team-name">{away_team}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Heutige Spiele anzeigen
    if today_matches:
        st.markdown("### 📅 Heute geplant")
        for match in today_matches:
            home_team = match['homeTeam']['name']
            away_team = match['awayTeam']['name']
            match_time = datetime.strptime(match['utcDate'], '%Y-%m-%dT%H:%M:%SZ')
            time_str = match_time.strftime('%H:%M')
            
            st.markdown(f"""
            <div class="match-card" style="background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%);">
                <div style="text-align: center; color: #fbbf24; margin-bottom: 8px;">⏰ {time_str} Uhr</div>
                <div class="team-name">{home_team}</div>
                <div style="text-align: center; font-size: 20px; margin: 10px 0;">vs</div>
                <div class="team-name">{away_team}</div>
            </div>
            """, unsafe_allow_html=True)
    
    if not live_matches and not today_matches:
        st.info("ℹ️ Heute keine Live-Spiele oder anstehenden Spiele")
    
    return matches

def display_standings(standings_data):
    """
    Zeigt die Gruppentabelle an (ohne Pandas)
    """
    if not standings_data or 'standings' not in standings_data:
        st.error("❌ Keine Tabellendaten verfügbar")
        return
    
    standings = standings_data['standings']
    
    if not standings:
        st.info("ℹ️ Tabelle noch nicht verfügbar")
        return
    
    # Nehme die erste Tabelle (Gesamttabelle)
    table = standings[0]['table']
    
    # Erstelle HTML Tabelle
    html = """
    <style>
    .standings-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 11px;
        background: white;
        border-radius: 8px;
        overflow: hidden;
    }
    .standings-table th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 8px 4px;
        text-align: left;
        font-weight: bold;
    }
    .standings-table td {
        padding: 6px 4px;
        border-bottom: 1px solid #e5e7eb;
    }
    .standings-table tr:hover {
        background: #f3f4f6;
    }
    .pos {
        font-weight: bold;
        color: #667eea;
    }
    </style>
    <table class="standings-table">
    <thead>
        <tr>
            <th>Pos</th>
            <th>Team</th>
            <th>Sp</th>
            <th>S</th>
            <th>U</th>
            <th>N</th>
            <th>Tore</th>
            <th>Pkt</th>
        </tr>
    </thead>
    <tbody>
    """
    
    for entry in table:
        team_name = entry['team']['name']
        # Kürze lange Namen
        if len(team_name) > 20:
            team_name = team_name[:17] + "..."
        
        html += f"""
        <tr>
            <td class="pos">{entry['position']}</td>
            <td>{team_name}</td>
            <td>{entry['playedGames']}</td>
            <td>{entry['won']}</td>
            <td>{entry['draw']}</td>
            <td>{entry['lost']}</td>
            <td>{entry['goalsFor']}:{entry['goalsAgainst']}</td>
            <td><strong>{entry['points']}</strong></td>
        </tr>
        """
    
    html += """
    </tbody>
    </table>
    """
    
    st.markdown(html, unsafe_allow_html=True)

# ============================================================================
# HAUPTPROGRAMM
# ============================================================================

def main():
    # Seitenkonfiguration
    st.set_page_config(
        page_title="⚽ Champions League LIVE",
        page_icon="⚽",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Custom CSS laden
    load_custom_css()
    
    # Header
    st.markdown("# ⚽ Champions League LIVE")
    st.markdown(f"*Letzte Aktualisierung: {datetime.now().strftime('%H:%M:%S')}*")
    
    # Auto-Refresh alle 30 Sekunden
    placeholder = st.empty()
    
    # Session State für vorherige Spielstände
    if 'previous_matches' not in st.session_state:
        st.session_state.previous_matches = None
    
    with placeholder.container():
        # Daten laden
        matches_data = get_api_data(MATCHES_URL)
        standings_data = get_api_data(STANDINGS_URL)
        
        if matches_data:
            current_matches = matches_data.get('matches', [])
            
            # Prüfe auf Tore
            check_for_goals(current_matches, st.session_state.previous_matches)
            
            # Speichere aktuelle Spielstände
            st.session_state.previous_matches = current_matches
        
        # Split-Screen Layout
        st.markdown('<div class="split-container">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="split-column">', unsafe_allow_html=True)
            st.markdown("## 🔥 Live-Spiele")
            display_matches(matches_data)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="split-column">', unsafe_allow_html=True)
            st.markdown("## 📊 Tabelle")
            display_standings(standings_data)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Auto-Refresh nach 30 Sekunden
    time.sleep(30)
    st.rerun()

if __name__ == "__main__":
    main()
