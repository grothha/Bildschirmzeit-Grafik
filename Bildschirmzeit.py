import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date, timedelta
import plotly.express as px

# --- KONFIGURATION ---
st.set_page_config(page_title="ScreenTime Tracker", layout="wide")

# --- DATENBANK LOGIK ---
def init_db():
    conn = sqlite3.connect("screentime.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sessions 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  date TEXT, start_time TEXT, end_time TEXT, duration_min REAL)''')
    conn.commit()
    return conn

def save_session(start_dt, end_dt):
    duration = (end_dt - start_dt).total_seconds() / 60
    conn = init_db()
    c = conn.cursor()
    c.execute("INSERT INTO sessions (date, start_time, end_time, duration_min) VALUES (?, ?, ?, ?)",
              (start_dt.date().isoformat(), start_dt.strftime("%H:%M:%S"), 
               end_dt.strftime("%H:%M:%S"), round(duration, 2)))
    conn.commit()
    conn.close()

def load_data():
    conn = init_db()
    df = pd.read_sql_query("SELECT * FROM sessions", conn)
    conn.close()
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
    return df

# --- UI LOGIK ---
def main():
    st.title("⏱️ ScreenTime Tracker")
    st.markdown("Verfolge und analysiere deine Nutzungszeit.")

    # Sidebar: Steuerung
    st.sidebar.header("Steuerung")
    
    if "tracking" not in st.session_state:
        st.session_state.tracking = False

    if not st.session_state.tracking:
        if st.sidebar.button("▶️ Session starten", use_container_width=True):
            st.session_state.start_time = datetime.now()
            st.session_state.tracking = True
            st.rerun()
    else:
        st.sidebar.warning("Tracking läuft...")
        start_time_display = st.session_state.start_time.strftime("%H:%M:%S")
        st.sidebar.info(f"Startzeit: {start_time_display}")
        
        if st.sidebar.button("⏹️ Session stoppen", use_container_width=True):
            end_time = datetime.now()
            save_session(st.session_state.start_time, end_time)
            st.session_state.tracking = False
            st.success("Session gespeichert!")
            st.rerun()

    # Daten laden
    df = load_data()

    # Hauptbereich: Metriken
    col1, col2, col3 = st.columns(3)
    
    if not df.empty:
        today = pd.to_datetime(date.today())
        last_7_days = today - timedelta(days=7)
        
        # Berechnung der Metriken
        daily_sum = df[df['date'] == today]['duration_min'].sum()
        weekly_sum = df[df['date'] >= last_7_days]['duration_min'].sum()
        avg_sum = df.groupby('date')['duration_min'].sum().mean()

        col1.metric("Heute", f"{int(daily_sum)} Min")
        col2.metric("Letzte 7 Tage", f"{int(weekly_sum)} Min")
        col3.metric("Ø pro Tag", f"{int(avg_sum)} Min")

        # Visualisierung
        st.subheader("Nutzungsverlauf")
        
        # Aggregation nach Tag für den Chart
        chart_data = df.groupby('date')['duration_min'].sum().reset_index()
        
        fig = px.bar(chart_data, x='date', y='duration_min', 
                     title="Bildschirmzeit pro Tag",
                     labels={'duration_min': 'Minuten', 'date': 'Datum'},
                     color_discrete_sequence=['#00CC96'])
        
        st.plotly_chart(fig, use_container_width=True)

        # Tabellarische Ansicht
        with st.expander("Rohdaten anzeigen"):
            st.dataframe(df.sort_values(by="date", ascending=False), use_container_width=True)
    else:
        st.info("Noch keine Daten vorhanden. Starte deine erste Session in der Sidebar!")

if __name__ == "__main__":
    main()
