import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Jahresplan Bildschirmzeit", layout="wide")

st.title("📊 Jahresplan deiner Bildschirmzeit")

st.markdown(
    "Diese App zeigt dir deine Bildschirmzeit über ein ganzes Jahr – "
    "nach Tagen und zusammengefasst nach Monaten."
)

# -----------------------------------
# Datenquelle auswählen
# -----------------------------------
st.sidebar.header("Datenquelle")
data_source = st.sidebar.radio(
    "Wie möchtest du deine Daten laden?",
    ("Demo-Daten verwenden", "CSV-Datei hochladen")
)

if data_source == "CSV-Datei hochladen":
    uploaded_file = st.sidebar.file_uploader(
        "CSV-Datei auswählen", type=["csv"]
    )

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, parse_dates=["date"])
    else:
        st.info("⬅️ Bitte lade eine CSV-Datei hoch.")
        st.stop()
else:
    # Demo-Daten erzeugen
    date_range = pd.date_range(start="2025-01-01", end="2025-12-31")
    df = pd.DataFrame({
        "date": date_range,
        "screen_time_hours": (
            2
            + (date_range.dayofyear % 5)
            + (date_range.dayofweek * 0.3)
        )
    })

# -----------------------------------
# Daten vorbereiten
# -----------------------------------
df["month"] = df["date"].dt.to_period("M")
monthly = df.groupby("month")["screen_time_hours"].sum()

# -----------------------------------
# Tagesansicht
# -----------------------------------
st.subheader("🗓️ Tagesansicht")

fig1, ax1 = plt.subplots(figsize=(12, 4))
ax1.plot(df["date"], df["screen_time_hours"])
ax1.set_ylabel("Stunden")
ax1.set_xlabel("Datum")
ax1.set_title("Tägliche Bildschirmzeit")
plt.xticks(rotation=45)

st.pyplot(fig1)

# -----------------------------------
# Monatsübersicht
# -----------------------------------
st.subheader("📆 Monatsübersicht (Jahresplan)")

fig2, ax2 = plt.subplots(figsize=(10, 5))
monthly.plot(kind="bar", ax=ax2)
ax2.set_ylabel("Gesamtstunden")
ax2.set_xlabel("Monat")
ax2.set_title("Bildschirmzeit pro Monat")

st.pyplot(fig2)

# -----------------------------------
# Statistiken
# -----------------------------------
st.subheader("📈 Statistiken")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Durchschnitt / Tag",
    f"{df['screen_time_hours'].mean():.2f} h"
)

col2.metric(
    "Maximaler Tag",
    f"{df['screen_time_hours'].max():.2f} h"
)

col3.metric(
    "Gesamt im Jahr",
    f"{df['screen_time_hours'].sum():.1f} h"
)

