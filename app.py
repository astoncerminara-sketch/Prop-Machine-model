# Your Personal Prop Machine - astoncerminara@gmail.com Edition
# Run on Streamlit Cloud: https://share.streamlit.io

import streamlit as st
import nfl_data_py as nfl
import pandas as pd
import numpy as np
from scipy import stats
import plotly.express as px  # For charts

st.set_page_config(page_title="Aston's Prop Machine", layout="wide")
st.title("🚀 Aston's NFL/NBA Prop Machine")
st.markdown("Built for astoncerminara@gmail.com | Monte Carlo Sims (10k iterations) | Edges >60% Flagged")

# Sidebar: Sport & Date Selector
sport = st.sidebar.selectbox("Sport", ["NFL", "NBA"])
if sport == "NFL":
    season = st.sidebar.number_input("Season", value=2025)
    week = st.sidebar.number_input("Week", value=12)
else:  # NBA
    season = st.sidebar.number_input("Season", value=2025)
    month = st.sidebar.selectbox("Month", [11, 12])  # Nov/Dec example
    day = st.sidebar.number_input("Day", value=25)

# Fetch Data (Live)
@st.cache_data(ttl=300)  # Refresh every 5 min
def load_data(sport, **kwargs):
    if sport == "NFL":
        schedule = nfl.import_schedules([kwargs['season']])
        week_games = schedule[(schedule['season'] == kwargs['season']) & (schedule['week'] == kwargs['week'])]
        rosters = nfl.import_rosters([kwargs['season']])
        weekly_stats = nfl.import_weekly_data([kwargs['season']])
        return week_games, rosters, weekly_stats
    else:  # NBA placeholder - expand with nba_api if needed
        # Mock NBA data for demo; replace with real API
        return pd.DataFrame({'games': ['ATL vs WSH']}), pd.DataFrame(), pd.DataFrame({'points': [20]})

data = load_data(sport, **locals())
st.success(f"Loaded {len(data[0])} {sport} games for {season}-{week if 'week' in locals() else f'{month}/{day}'}")

# Simulation Function
def simulate_prop(mean, std_dev, line, dist='normal', iterations=10000):
    if dist == 'normal':
        sims = np.random.normal(mean, std_dev, iterations)
    else:  # Poisson for TDs/Points
        sims = np.random.poisson(mean, iterations)
    over_prob = np.mean(sims > line) * 100
    return np.mean(sims), over_prob

# Generate Props (Simplified for NFL; Adapt for NBA)
if st.button("Run Simulations & Get Props"):
    props = []
    for _, game in data[0].head(2).iterrows():  # Demo: Top 2 games
        # Mock player loop - expand with real roster/stats
        players = [{'name': 'Saquon Barkley', 'pos': 'RB', 'baseline': 80, 'opp_allowed': 100}]
        for p in players:
            adj_mean = (p['baseline'] + p['opp_allowed']) / 2
            std_dev = adj_mean * 0.3
            line = 88.5
            proj, hit = simulate_prop(adj_mean, std_dev, line)
            props.append({
                'Game': f"{game['away_team']} @ {game['home_team']}",
                'Player': p['name'],
                'Prop': f"{p['pos']} Yards Over {line}",
                'Proj Mean': round(proj, 1),
                'Hit Prob (%)': round(hit, 1),
                'Recommended': 'Yes' if hit > 55 else 'No'
            })
    
    df = pd.DataFrame(props)
    st.dataframe(df, use_container_width=True)
    
    # Parlay Builder
    edges = df[df['Recommended'] == 'Yes'].head(3)
    if not edges.empty:
        st.subheader("Top 3-Leg Parlay")
        st.dataframe(edges)
        st.metric("Est. Payout (+600 odds)", "$600 on $100 bet")
    
    # Export
    st.download_button("Download CSV", df.to_csv(index=False), "props.csv")

# Footer
st.markdown("---")
st.caption("Powered by Streamlit | Data: NFL/nba_api | Built for Aston Cerminara")
