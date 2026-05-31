import os
from datetime import datetime, timezone

import altair as alt
import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="Live Sports Predictions Demo",
    page_icon="⚽",
    layout="wide",
)

# =========================================================
# Config
# =========================================================
def get_secret(name: str, default: str = "") -> str:
    env_value = os.getenv(name, "")
    if env_value:
        return env_value

    try:
        return str(st.secrets[name])
    except Exception:
        return default


FOOTBALL_API_KEY = get_secret("FOOTBALL_DATA_API_KEY")
BALLDONTLIE_API_KEY = get_secret("BALLDONTLIE_API_KEY")

FOOTBALL_BASE = "https://api.football-data.org/v2"
BALLDONTLIE_GAMES_URL = "https://api.balldontlie.io/v1/games"

FOOTBALL_COMPETITIONS = {
    "PL": "Premier League",
    "PD": "La Liga",
    "SA": "Serie A",
    "BL1": "Bundesliga",
}

# =========================================================
# Fallback sample data
# =========================================================
def sample_football_df():
    return pd.DataFrame(
        [
            {
                "Date": "2026-05-22",
                "League": "Premier League",
                "Match": "Arsenal vs Chelsea",
                "Status": "SCHEDULED",
                "Pick": "Home or Draw",
                "Confidence": 54,
                "Model Edge": 1.2,
                "Source": "sample",
            },
            {
                "Date": "2026-05-22",
                "League": "La Liga",
                "Match": "Barcelona vs Sevilla",
                "Status": "SCHEDULED",
                "Pick": "Home or Draw",
                "Confidence": 55,
                "Model Edge": 1.4,
                "Source": "sample",
            },
        ]
    )


def sample_basketball_df():
    return pd.DataFrame(
        [
            {
                "Date": "2026-05-22",
                "League": "NBA",
                "Match": "Celtics vs Heat",
                "Status": "SCHEDULED",
                "Pick": "Home Moneyline",
                "Confidence": 57,
                "Model Edge": 1.8,
                "Source": "sample",
            },
            {
                "Date": "2026-05-22",
                "League": "NBA",
                "Match": "Lakers vs Suns",
                "Status": "SCHEDULED",
                "Pick": "Home Moneyline",
                "Confidence": 56,
                "Model Edge": 1.5,
                "Source": "sample",
            },
        ]
    )


# =========================================================
# Utilities
# =========================================================
def parse_iso_date(dt_str: str):
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except Exception:
        return None


def safe_get_json(url: str, headers: dict | None = None, params: dict | None = None):
    response = requests.get(url, headers=headers, params=params, timeout=20)
    response.raise_for_status()
    return response.json()


def demo_pick_for_football():
    # TODO: replace with your actual model
    return "Home or Draw", 54, 1.2


def demo_pick_for_basketball():
    # TODO: replace with your actual model
    return "Home Moneyline", 57, 1.8


# =========================================================
# Live API fetchers
# =========================================================
@st.cache_data(ttl=900)
def fetch_football_matches():
    if not FOOTBALL_API_KEY:
        return sample_football_df(), "Missing FOOTBALL_DATA_API_KEY — showing sample football data."

    rows = []
    headers = {"X-Auth-Token": FOOTBALL_API_KEY}

    try:
        for code, league_name in FOOTBALL_COMPETITIONS.items():
            url = f"{FOOTBALL_BASE}/competitions/{code}/matches"
            payload = safe_get_json(url, headers=headers)

            matches = payload.get("matches", [])
            now_utc = datetime.now(timezone.utc)

            for m in matches:
                utc_date = parse_iso_date(m.get("utcDate"))
                if utc_date is None:
                    continue

                if utc_date.date() < now_utc.date():
                    continue

                home = (m.get("homeTeam") or {}).get("name", "Home")
                away = (m.get("awayTeam") or {}).get("name", "Away")
                status = m.get("status", "UNKNOWN")

                pick, conf, edge = demo_pick_for_football()

                rows.append(
                    {
                        "Date": utc_date.strftime("%Y-%m-%d %H:%M UTC"),
                        "League": league_name,
                        "Match": f"{home} vs {away}",
                        "Status": status,
                        "Pick": pick,
                        "Confidence": conf,
                        "Model Edge": edge,
                        "Source": "live",
                    }
                )

        if not rows:
            return sample_football_df(), "Football API returned no upcoming rows — showing sample football data."

        df = pd.DataFrame(rows).sort_values("Date").reset_index(drop=True)
        return df, "Live football data loaded."

    except Exception as e:
        return sample_football_df(), f"Football API error: {e} — showing sample football data."


@st.cache_data(ttl=900)
def fetch_basketball_games():
    if not BALLDONTLIE_API_KEY:
        return sample_basketball_df(), "Missing BALLDONTLIE_API_KEY — showing sample basketball data."

    try:
        headers = {"Authorization": BALLDONTLIE_API_KEY}
        payload = safe_get_json(BALLDONTLIE_GAMES_URL, headers=headers)

        games = payload.get("data", [])
        now_utc = datetime.now(timezone.utc)
        rows = []

        for g in games:
            game_dt = parse_iso_date(g.get("date"))
            if game_dt is None:
                continue

            if game_dt.date() < now_utc.date():
                continue

            home_team = ((g.get("home_team") or {}).get("full_name")) or "Home"
            away_team = ((g.get("visitor_team") or {}).get("full_name")) or "Away"
            status = g.get("status", "UNKNOWN")

            pick, conf, edge = demo_pick_for_basketball()

            rows.append(
                {
                    "Date": game_dt.strftime("%Y-%m-%d %H:%M UTC"),
                    "League": "NBA",
                    "Match": f"{home_team} vs {away_team}",
                    "Status": status,
                    "Pick": pick,
                    "Confidence": conf,
                    "Model Edge": edge,
                    "Source": "live",
                }
            )

        if not rows:
            return sample_basketball_df(), "Basketball API returned no upcoming rows — showing sample basketball data."

        df = pd.DataFrame(rows).sort_values("Date").reset_index(drop=True)
        return df, "Live basketball data loaded."

    except Exception as e:
        return sample_basketball_df(), f"Basketball API error: {e} — showing sample basketball data."


# =========================================================
# Load data
# =========================================================
football_df, football_msg = fetch_football_matches()
basketball_df, basketball_msg = fetch_basketball_games()

history_df = pd.DataFrame(
    [
        {"Date": "2026-05-15", "Sport": "Football", "Correct": 1},
        {"Date": "2026-05-16", "Sport": "Football", "Correct": 0},
        {"Date": "2026-05-17", "Sport": "Football", "Correct": 1},
        {"Date": "2026-05-18", "Sport": "Football", "Correct": 1},
        {"Date": "2026-05-19", "Sport": "Football", "Correct": 0},
        {"Date": "2026-05-15", "Sport": "Basketball", "Correct": 1},
        {"Date": "2026-05-16", "Sport": "Basketball", "Correct": 1},
        {"Date": "2026-05-17", "Sport": "Basketball", "Correct": 0},
        {"Date": "2026-05-18", "Sport": "Basketball", "Correct": 1},
        {"Date": "2026-05-19", "Sport": "Basketball", "Correct": 1},
    ]
)
history_df["Date"] = pd.to_datetime(history_df["Date"])

# =========================================================
# Sidebar
# =========================================================
st.sidebar.title("⚙️ Controls")
sport = st.sidebar.selectbox("Sport", ["All", "Football", "Basketball"])
min_conf = st.sidebar.slider("Minimum confidence", 50, 90, 54)
show_raw = st.sidebar.checkbox("Show raw data", value=False)

st.sidebar.markdown("---")
st.sidebar.caption("Prediction columns are demo heuristics until you plug in your own model.")

# =========================================================
# Header
# =========================================================
st.title("⚽🏀 Live Sports Prediction Dashboard")
st.markdown(
    "Live fixtures/games from APIs, with placeholder prediction columns so you can see the full UI flow."
)

c1, c2 = st.columns(2)
with c1:
    st.info(football_msg)
with c2:
    st.info(basketball_msg)

# =========================================================
# KPIs
# =========================================================
football_filtered = football_df[football_df["Confidence"] >= min_conf]
basketball_filtered = basketball_df[basketball_df["Confidence"] >= min_conf]

if sport == "Football":
    combined = football_filtered.copy()
elif sport == "Basketball":
    combined = basketball_filtered.copy()
else:
    combined = pd.concat([football_filtered, basketball_filtered], ignore_index=True)

total_picks = len(combined)
avg_conf = combined["Confidence"].mean() if total_picks else 0
best_edge = combined["Model Edge"].max() if total_picks else 0

k1, k2, k3 = st.columns(3)
k1.metric("Picks Shown", total_picks)
k2.metric("Average Confidence", f"{avg_conf:.1f}%")
k3.metric("Best Model Edge", f"{best_edge:.1f}%")

st.markdown("---")

# =========================================================
# Tabs
# =========================================================
tab1, tab2, tab3 = st.tabs(["Today's Picks", "Performance", "API Notes"])

with tab1:
    if sport in ["All", "Football"]:
        st.subheader("Football")
        st.dataframe(football_filtered, use_container_width=True, hide_index=True)

    if sport in ["All", "Basketball"]:
        st.subheader("Basketball")
        st.dataframe(basketball_filtered, use_container_width=True, hide_index=True)

    st.subheader("Top Picks by Confidence")

    top_frames = []
    if sport in ["All", "Football"] and not football_filtered.empty:
        top_frames.append(
            football_filtered[["Match", "Pick", "Confidence"]].assign(Sport="Football")
        )
    if sport in ["All", "Basketball"] and not basketball_filtered.empty:
        top_frames.append(
            basketball_filtered[["Match", "Pick", "Confidence"]].assign(Sport="Basketball")
        )

    if top_frames:
        top_df = pd.concat(top_frames, ignore_index=True).sort_values("Confidence", ascending=False)

        chart = (
            alt.Chart(top_df)
            .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
            .encode(
                x=alt.X("Confidence:Q", scale=alt.Scale(domain=[0, 100])),
                y=alt.Y("Match:N", sort="-x"),
                color="Sport:N",
                tooltip=["Sport", "Match", "Pick", "Confidence"],
            )
            .properties(height=320)
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.warning("No rows meet the selected confidence threshold.")

with tab2:
    st.subheader("Demo Accuracy View")
    acc_df = (
        history_df.groupby("Sport", as_index=False)["Correct"].mean()
        .assign(Accuracy=lambda d: d["Correct"] * 100)
    )

    c1, c2 = st.columns(2)

    with c1:
        acc_chart = (
            alt.Chart(acc_df)
            .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
            .encode(
                x="Sport:N",
                y=alt.Y("Accuracy:Q", scale=alt.Scale(domain=[0, 100])),
                color="Sport:N",
                tooltip=["Sport", alt.Tooltip("Accuracy:Q", format=".1f")],
            )
            .properties(height=300)
        )
        st.altair_chart(acc_chart, use_container_width=True)

    with c2:
        daily = (
            history_df.groupby(["Date", "Sport"], as_index=False)["Correct"].mean()
            .assign(Accuracy=lambda d: d["Correct"] * 100)
        )

        line_chart = (
            alt.Chart(daily)
            .mark_line(point=True)
            .encode(
                x="Date:T",
                y=alt.Y("Accuracy:Q", scale=alt.Scale(domain=[0, 100])),
                color="Sport:N",
                tooltip=["Date", "Sport", alt.Tooltip("Accuracy:Q", format=".1f")],
            )
            .properties(height=300)
        )
        st.altair_chart(line_chart, use_container_width=True)

    st.caption("Performance numbers remain demo values until you connect your own prediction outputs.")

with tab3:
    st.subheader("Live API fetching code")
    st.code(
        '''headers = {"X-Auth-Token": FOOTBALL_API_KEY}
football_payload = safe_get_json(
    f"{FOOTBALL_BASE}/competitions/PL/matches",
    headers=headers,
)

basketball_headers = {"Authorization": BALLDONTLIE_API_KEY}
basketball_payload = safe_get_json(
    BALLDONTLIE_GAMES_URL,
    headers=basketball_headers,
)''',
        language="python",
    )

    st.subheader("Secrets / Environment Variables")
    st.code(
        """# Streamlit Cloud secrets.toml
FOOTBALL_DATA_API_KEY = "your_football_data_key"
BALLDONTLIE_API_KEY = "your_balldontlie_key"

# or local shell environment variables
# export FOOTBALL_DATA_API_KEY="your_football_data_key"
# export BALLDONTLIE_API_KEY="your_balldontlie_key""",
        language="toml",
    )

    st.subheader("What is live vs demo")
    st.markdown(
        """
- **Live:** fixture/game schedule rows
- **Demo:** pick, confidence, and model edge columns
- **Next step:** replace `demo_pick_for_football()` and `demo_pick_for_basketball()` with your actual model
        """
    )

    st.subheader("Optional odds integration")
    st.markdown(
        "Add live odds next if you want h2h, spreads, and totals in the same dashboard."
    )

if show_raw:
    st.markdown("---")
    st.subheader("Raw Data")
    c1, c2 = st.columns(2)
    with c1:
        st.write("Football")
        st.dataframe(football_df, use_container_width=True, hide_index=True)
    with c2:
        st.write("Basketball")
        st.dataframe(basketball_df, use_container_width=True, hide_index=True)
