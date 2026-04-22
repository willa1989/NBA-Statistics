import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import requests
import time

# ── Config ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NBA Playoffs Analyzer",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0a0a0a; }
    .block-container { padding-top: 1rem; padding-bottom: 2rem; max-width: 1200px; }
    div[data-testid="metric-container"] {
        background: #1a1a2e;
        border: 1px solid #16213e;
        border-radius: 12px;
        padding: 1rem 1.2rem;
    }
    div[data-testid="metric-container"] label { color: #8888aa !important; font-size: 12px; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        font-size: 1.8rem; font-weight: 700; color: #ffffff;
    }
    .prob-bar-container {
        background: #1a1a2e; border-radius: 12px;
        padding: 1.5rem; margin: 1rem 0;
    }
    .team-header {
        font-size: 1.4rem; font-weight: 700;
        margin-bottom: 0.2rem; color: #ffffff;
    }
    .section-title {
        font-size: 1rem; font-weight: 600;
        color: #8888aa; text-transform: uppercase;
        letter-spacing: 0.08em; margin: 1.5rem 0 0.8rem;
    }
    .stSelectbox label, .stSlider label { color: #8888aa !important; font-size: 12px; }
    div[data-baseweb="select"] > div {
        background-color: #1a1a2e !important;
        border-color: #333366 !important; color: #fff !important;
    }
    .stTabs [data-baseweb="tab"] { color: #8888aa; }
    .stTabs [aria-selected="true"] { color: #4fa8ff; }
    .stTabs [data-baseweb="tab-highlight"] { background-color: #4fa8ff; }
    hr { border-color: #1e1e3a; }
</style>
""", unsafe_allow_html=True)

# ── NBA Teams data (logos, colors, conference) ────────────────────────────────
TEAMS = {
    # East
    "Boston Celtics":         {"color": "#007A33", "conf": "East", "abbr": "BOS"},
    "New York Knicks":        {"color": "#F58426", "conf": "East", "abbr": "NYK"},
    "Milwaukee Bucks":        {"color": "#00471B", "conf": "East", "abbr": "MIL"},
    "Cleveland Cavaliers":    {"color": "#860038", "conf": "East", "abbr": "CLE"},
    "Indiana Pacers":         {"color": "#002D62", "conf": "East", "abbr": "IND"},
    "Philadelphia 76ers":     {"color": "#006BB6", "conf": "East", "abbr": "PHI"},
    "Miami Heat":             {"color": "#98002E", "conf": "East", "abbr": "MIA"},
    "Chicago Bulls":          {"color": "#CE1141", "conf": "East", "abbr": "CHI"},
    # West
    "Oklahoma City Thunder":  {"color": "#007AC1", "conf": "West", "abbr": "OKC"},
    "Denver Nuggets":         {"color": "#0E2240", "conf": "West", "abbr": "DEN"},
    "Minnesota Timberwolves": {"color": "#0C2340", "conf": "West", "abbr": "MIN"},
    "Los Angeles Lakers":     {"color": "#552583", "conf": "West", "abbr": "LAL"},
    "Golden State Warriors":  {"color": "#1D428A", "conf": "West", "abbr": "GSW"},
    "Dallas Mavericks":       {"color": "#00538C", "conf": "West", "abbr": "DAL"},
    "Memphis Grizzlies":      {"color": "#5D76A9", "conf": "West", "abbr": "MEM"},
    "Sacramento Kings":       {"color": "#5A2D81", "conf": "West", "abbr": "SAC"},
}

TEAM_NAMES = list(TEAMS.keys())

# ── Mock stats (used as fallback / demo) ──────────────────────────────────────
MOCK_STATS = {
    "Boston Celtics":         {"off_rtg": 121.5, "def_rtg": 107.2, "net_rtg": 14.3, "pace": 98.1, "ts_pct": 60.2, "reb_pct": 51.8, "ast_ratio": 19.4, "tov_ratio": 12.1, "three_pct": 38.9, "clutch_net": 12.1, "rest_days": 2, "injuries": 0},
    "New York Knicks":        {"off_rtg": 114.8, "def_rtg": 111.3, "net_rtg":  3.5, "pace": 95.4, "ts_pct": 56.1, "reb_pct": 52.3, "ast_ratio": 16.8, "tov_ratio": 13.5, "three_pct": 35.2, "clutch_net":  4.2, "rest_days": 1, "injuries": 1},
    "Milwaukee Bucks":        {"off_rtg": 117.6, "def_rtg": 112.8, "net_rtg":  4.8, "pace": 100.2, "ts_pct": 57.8, "reb_pct": 50.9, "ast_ratio": 18.1, "tov_ratio": 14.2, "three_pct": 36.4, "clutch_net":  3.8, "rest_days": 2, "injuries": 2},
    "Cleveland Cavaliers":    {"off_rtg": 116.2, "def_rtg": 109.5, "net_rtg":  6.7, "pace": 96.8, "ts_pct": 57.2, "reb_pct": 53.1, "ast_ratio": 20.1, "tov_ratio": 11.8, "three_pct": 37.1, "clutch_net":  5.5, "rest_days": 3, "injuries": 0},
    "Indiana Pacers":         {"off_rtg": 119.3, "def_rtg": 115.4, "net_rtg":  3.9, "pace": 104.5, "ts_pct": 58.9, "reb_pct": 49.8, "ast_ratio": 22.3, "tov_ratio": 15.1, "three_pct": 37.8, "clutch_net":  1.9, "rest_days": 1, "injuries": 1},
    "Philadelphia 76ers":     {"off_rtg": 115.1, "def_rtg": 113.6, "net_rtg":  1.5, "pace": 97.3, "ts_pct": 56.8, "reb_pct": 51.4, "ast_ratio": 17.5, "tov_ratio": 13.8, "three_pct": 35.9, "clutch_net":  0.8, "rest_days": 2, "injuries": 3},
    "Miami Heat":             {"off_rtg": 113.4, "def_rtg": 111.8, "net_rtg":  1.6, "pace": 96.1, "ts_pct": 55.4, "reb_pct": 50.2, "ast_ratio": 17.9, "tov_ratio": 12.4, "three_pct": 34.8, "clutch_net":  6.4, "rest_days": 2, "injuries": 1},
    "Chicago Bulls":          {"off_rtg": 112.7, "def_rtg": 114.2, "net_rtg": -1.5, "pace": 98.4, "ts_pct": 55.1, "reb_pct": 50.5, "ast_ratio": 16.4, "tov_ratio": 14.3, "three_pct": 34.2, "clutch_net": -1.2, "rest_days": 1, "injuries": 2},
    "Oklahoma City Thunder":  {"off_rtg": 120.8, "def_rtg": 108.4, "net_rtg": 12.4, "pace": 99.5, "ts_pct": 59.6, "reb_pct": 52.7, "ast_ratio": 21.2, "tov_ratio": 11.5, "three_pct": 38.2, "clutch_net": 10.3, "rest_days": 2, "injuries": 0},
    "Denver Nuggets":         {"off_rtg": 119.4, "def_rtg": 111.6, "net_rtg":  7.8, "pace": 97.8, "ts_pct": 59.1, "reb_pct": 51.6, "ast_ratio": 23.4, "tov_ratio": 12.8, "three_pct": 37.5, "clutch_net":  7.2, "rest_days": 3, "injuries": 1},
    "Minnesota Timberwolves": {"off_rtg": 115.7, "def_rtg": 108.9, "net_rtg":  6.8, "pace": 98.3, "ts_pct": 57.3, "reb_pct": 52.4, "ast_ratio": 18.6, "tov_ratio": 13.2, "three_pct": 36.8, "clutch_net":  5.1, "rest_days": 2, "injuries": 1},
    "Los Angeles Lakers":     {"off_rtg": 116.9, "def_rtg": 113.5, "net_rtg":  3.4, "pace": 99.1, "ts_pct": 57.9, "reb_pct": 50.8, "ast_ratio": 19.8, "tov_ratio": 14.1, "three_pct": 36.2, "clutch_net":  4.6, "rest_days": 1, "injuries": 2},
    "Golden State Warriors":  {"off_rtg": 118.2, "def_rtg": 114.1, "net_rtg":  4.1, "pace": 101.3, "ts_pct": 58.4, "reb_pct": 50.1, "ast_ratio": 22.8, "tov_ratio": 14.8, "three_pct": 39.1, "clutch_net":  3.9, "rest_days": 2, "injuries": 2},
    "Dallas Mavericks":       {"off_rtg": 118.8, "def_rtg": 113.7, "net_rtg":  5.1, "pace": 97.6, "ts_pct": 58.7, "reb_pct": 49.7, "ast_ratio": 18.3, "tov_ratio": 13.4, "three_pct": 38.5, "clutch_net":  4.8, "rest_days": 2, "injuries": 1},
    "Memphis Grizzlies":      {"off_rtg": 113.1, "def_rtg": 114.8, "net_rtg": -1.7, "pace": 102.4, "ts_pct": 54.8, "reb_pct": 53.2, "ast_ratio": 17.4, "tov_ratio": 15.6, "three_pct": 33.5, "clutch_net": -2.1, "rest_days": 1, "injuries": 3},
    "Sacramento Kings":       {"off_rtg": 116.3, "def_rtg": 115.2, "net_rtg":  1.1, "pace": 103.1, "ts_pct": 57.1, "reb_pct": 49.3, "ast_ratio": 21.5, "tov_ratio": 14.9, "three_pct": 36.5, "clutch_net":  0.5, "rest_days": 2, "injuries": 1},
}

# ── Probability model ─────────────────────────────────────────────────────────
def calc_win_prob(t1: str, t2: str, home: str, n_sim: int = 10000) -> dict:
    s1 = MOCK_STATS[t1]
    s2 = MOCK_STATS[t2]

    # Base net rating differential
    net_diff = s1["net_rtg"] - s2["net_rtg"]

    # Adjustments
    home_bonus = 3.5 if home == t1 else (-3.5 if home == t2 else 0)
    rest_bonus = (s1["rest_days"] - s2["rest_days"]) * 0.4
    injury_pen = (s2["injuries"] - s1["injuries"]) * 1.2
    clutch_bonus = (s1["clutch_net"] - s2["clutch_net"]) * 0.15

    adjusted_diff = net_diff + home_bonus + rest_bonus + injury_pen + clutch_bonus

    # Logistic → probability
    base_prob = 1 / (1 + np.exp(-adjusted_diff * 0.15))

    # Monte Carlo simulation of best-of-7
    np.random.seed(42)
    t1_wins_series = 0
    game_margins = []

    for _ in range(n_sim):
        w1, w2 = 0, 0
        while w1 < 4 and w2 < 4:
            home_adv = 3.5 if (w1 + w2) % 2 == 0 else -3.5
            p = 1 / (1 + np.exp(-(adjusted_diff + home_adv) * 0.15))
            noise = np.random.normal(0, 0.05)
            if np.random.random() < min(max(p + noise, 0.05), 0.95):
                w1 += 1
            else:
                w2 += 1
        if w1 == 4:
            t1_wins_series += 1
            game_margins.append(w1 - w2)

    series_prob = t1_wins_series / n_sim

    # Series length distribution
    def sim_series_length(p, n=n_sim):
        lengths = {4: 0, 5: 0, 6: 0, 7: 0}
        for _ in range(n):
            w1, w2 = 0, 0
            while w1 < 4 and w2 < 4:
                if np.random.random() < p:
                    w1 += 1
                else:
                    w2 += 1
            lengths[w1 + w2] += 1
        return {k: v / n * 100 for k, v in lengths.items()}

    length_dist = sim_series_length(base_prob)

    return {
        "prob_t1": round(series_prob * 100, 1),
        "prob_t2": round((1 - series_prob) * 100, 1),
        "game_prob_t1": round(base_prob * 100, 1),
        "net_diff": round(adjusted_diff, 2),
        "home_bonus": round(home_bonus, 1),
        "rest_bonus": round(rest_bonus, 1),
        "injury_pen": round(injury_pen, 1),
        "clutch_bonus": round(clutch_bonus, 2),
        "length_dist": length_dist,
    }


# ── Radar chart ───────────────────────────────────────────────────────────────
def radar_chart(t1: str, t2: str):
    categories = ["Off Rating", "Def Rating\n(inv)", "3P%", "Rebound%", "Assist Ratio", "Clutch Net"]
    s1, s2 = MOCK_STATS[t1], MOCK_STATS[t2]

    def normalize(v, lo, hi):
        return round((v - lo) / (hi - lo) * 10, 2)

    def vals(s):
        return [
            normalize(s["off_rtg"],    108, 124),
            normalize(130 - s["def_rtg"], 108, 130 - 105),
            normalize(s["three_pct"],  32, 41),
            normalize(s["reb_pct"],    48, 55),
            normalize(s["ast_ratio"],  15, 25),
            normalize(s["clutch_net"], -5, 15),
        ]

    v1, v2 = vals(s1), vals(s2)
    c1, c2 = TEAMS[t1]["color"], TEAMS[t2]["color"]

    fig = go.Figure()
    for vals_list, name, color in [(v1, t1, c1), (v2, t2, c2)]:
        vals_closed = vals_list + [vals_list[0]]
        cats_closed = categories + [categories[0]]
        fig.add_trace(go.Scatterpolar(
            r=vals_closed, theta=cats_closed, fill="toself",
            name=name, line=dict(color=color, width=2),
            fillcolor=color + "40",
        ))

    fig.update_layout(
        polar=dict(
            bgcolor="#0a0a0a",
            radialaxis=dict(visible=True, range=[0, 10], gridcolor="#1e1e3a", color="#444"),
            angularaxis=dict(gridcolor="#1e1e3a", color="#888"),
        ),
        paper_bgcolor="#0a0a0a", plot_bgcolor="#0a0a0a",
        showlegend=True,
        legend=dict(font=dict(color="#ccc"), bgcolor="#0a0a0a"),
        margin=dict(t=40, b=40, l=60, r=60),
        height=400,
    )
    return fig


# ── Bar comparison chart ──────────────────────────────────────────────────────
def bar_compare(t1: str, t2: str):
    s1, s2 = MOCK_STATS[t1], MOCK_STATS[t2]
    metrics = {
        "Off Rating":  ("off_rtg",   None),
        "Def Rating":  ("def_rtg",   "lower_better"),
        "Net Rating":  ("net_rtg",   None),
        "3P%":         ("three_pct", None),
        "TS%":         ("ts_pct",    None),
        "Clutch Net":  ("clutch_net",None),
    }

    labels = list(metrics.keys())
    v1 = [s1[metrics[m][0]] for m in labels]
    v2 = [s2[metrics[m][0]] for m in labels]

    fig = go.Figure()
    fig.add_trace(go.Bar(name=t1, x=labels, y=v1, marker_color=TEAMS[t1]["color"], opacity=0.9))
    fig.add_trace(go.Bar(name=t2, x=labels, y=v2, marker_color=TEAMS[t2]["color"], opacity=0.9))

    fig.update_layout(
        barmode="group",
        paper_bgcolor="#0a0a0a", plot_bgcolor="#0a0a0a",
        font=dict(color="#ccc"),
        xaxis=dict(gridcolor="#1e1e3a"),
        yaxis=dict(gridcolor="#1e1e3a"),
        legend=dict(bgcolor="#0a0a0a"),
        margin=dict(t=20, b=20, l=40, r=20),
        height=340,
    )
    return fig


# ── Series length distribution chart ─────────────────────────────────────────
def series_length_chart(length_dist: dict, t1: str, t2: str):
    games = [f"Game {k}" for k in length_dist.keys()]
    probs = list(length_dist.values())

    fig = go.Figure(go.Bar(
        x=games, y=probs,
        marker_color=["#4fa8ff", "#5fb87f", "#f5a623", "#e84040"],
        text=[f"{p:.1f}%" for p in probs],
        textposition="outside", textfont=dict(color="#ccc"),
    ))
    fig.update_layout(
        paper_bgcolor="#0a0a0a", plot_bgcolor="#0a0a0a",
        font=dict(color="#ccc"),
        yaxis=dict(gridcolor="#1e1e3a", title="Probabilidade (%)"),
        margin=dict(t=20, b=20, l=40, r=20),
        height=280,
        showlegend=False,
    )
    return fig


# ── All-teams Net Rating leaderboard ─────────────────────────────────────────
def leaderboard_chart():
    teams_sorted = sorted(MOCK_STATS.items(), key=lambda x: x[1]["net_rtg"], reverse=True)
    names = [t[0] for t in teams_sorted]
    nets  = [t[1]["net_rtg"] for t in teams_sorted]
    colors = [TEAMS[n]["color"] for n in names]

    fig = go.Figure(go.Bar(
        x=nets, y=[TEAMS[n]["abbr"] for n in names],
        orientation="h",
        marker_color=colors,
        text=[f"{v:+.1f}" for v in nets],
        textposition="auto",
        textfont=dict(color="#fff"),
    ))
    fig.update_layout(
        paper_bgcolor="#0a0a0a", plot_bgcolor="#0a0a0a",
        font=dict(color="#ccc"),
        xaxis=dict(gridcolor="#1e1e3a", title="Net Rating"),
        yaxis=dict(gridcolor="#1e1e3a"),
        margin=dict(t=20, b=20, l=50, r=20),
        height=520,
        showlegend=False,
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# LAYOUT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("# 🏀 NBA Playoffs Analyzer")
st.markdown("<p style='color:#8888aa;margin-top:-0.8rem'>Análise de confrontos, probabilidades e métricas avançadas</p>", unsafe_allow_html=True)
st.divider()

tabs = st.tabs(["⚔️  Confronto direto", "📊  Ranking geral", "🎯  Probabilidade de série"])

# ── TAB 1: Head-to-head ───────────────────────────────────────────────────────
with tabs[0]:
    col_sel1, col_sel2, col_sel3 = st.columns(3)
    with col_sel1:
        t1 = st.selectbox("Time 1 (favorito)", TEAM_NAMES, index=0)
    with col_sel2:
        t2 = st.selectbox("Time 2 (adversário)", TEAM_NAMES, index=8)
    with col_sel3:
        home_options = [t1, t2, "Neutro"]
        home = st.selectbox("Mando de quadra (jogo 1)", home_options, index=0)
        home_team = home if home != "Neutro" else None

    s1, s2 = MOCK_STATS[t1], MOCK_STATS[t2]

    st.divider()

    # Métricas
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<p class='team-header' style='color:{TEAMS[t1]['color']}'>{t1}</p>", unsafe_allow_html=True)
        mc1, mc2, mc3, mc4 = st.columns(4)
        mc1.metric("Off Rating",  f"{s1['off_rtg']:.1f}")
        mc2.metric("Def Rating",  f"{s1['def_rtg']:.1f}")
        mc3.metric("Net Rating",  f"{s1['net_rtg']:+.1f}")
        mc4.metric("Clutch Net",  f"{s1['clutch_net']:+.1f}")
    with col2:
        st.markdown(f"<p class='team-header' style='color:{TEAMS[t2]['color']}'>{t2}</p>", unsafe_allow_html=True)
        mc1, mc2, mc3, mc4 = st.columns(4)
        mc1.metric("Off Rating",  f"{s2['off_rtg']:.1f}")
        mc2.metric("Def Rating",  f"{s2['def_rtg']:.1f}")
        mc3.metric("Net Rating",  f"{s2['net_rtg']:+.1f}")
        mc4.metric("Clutch Net",  f"{s2['clutch_net']:+.1f}")

    st.markdown("<p class='section-title'>Comparativo de métricas</p>", unsafe_allow_html=True)
    st.plotly_chart(bar_compare(t1, t2), use_container_width=True)

    st.markdown("<p class='section-title'>Radar de performance</p>", unsafe_allow_html=True)
    st.plotly_chart(radar_chart(t1, t2), use_container_width=True)

    # Context info
    st.markdown("<p class='section-title'>Contexto do confronto</p>", unsafe_allow_html=True)
    cx1, cx2, cx3, cx4 = st.columns(4)
    cx1.metric("Descanso " + TEAMS[t1]["abbr"], f"{s1['rest_days']} dias")
    cx2.metric("Lesões " + TEAMS[t1]["abbr"],  f"{s1['injuries']} jogadores")
    cx3.metric("Descanso " + TEAMS[t2]["abbr"], f"{s2['rest_days']} dias")
    cx4.metric("Lesões " + TEAMS[t2]["abbr"],  f"{s2['injuries']} jogadores")


# ── TAB 2: Ranking geral ──────────────────────────────────────────────────────
with tabs[1]:
    st.markdown("<p class='section-title'>Net Rating — todos os times (playoffs 2025)</p>", unsafe_allow_html=True)
    st.plotly_chart(leaderboard_chart(), use_container_width=True)

    st.markdown("<p class='section-title'>Tabela completa de métricas</p>", unsafe_allow_html=True)
    df = pd.DataFrame([
        {
            "Time": t,
            "Conf": TEAMS[t]["conf"],
            "Off Rtg": s["off_rtg"],
            "Def Rtg": s["def_rtg"],
            "Net Rtg": s["net_rtg"],
            "Pace": s["pace"],
            "TS%": s["ts_pct"],
            "3P%": s["three_pct"],
            "Reb%": s["reb_pct"],
            "Clutch Net": s["clutch_net"],
            "Lesões": s["injuries"],
        }
        for t, s in sorted(MOCK_STATS.items(), key=lambda x: x[1]["net_rtg"], reverse=True)
    ])
    st.dataframe(
        df.style.background_gradient(subset=["Net Rtg"], cmap="RdYlGn"),
        use_container_width=True, hide_index=True,
    )


# ── TAB 3: Probabilidade de série ─────────────────────────────────────────────
with tabs[2]:
    st.markdown("**Configure o confronto e simule a série**")
    pc1, pc2, pc3 = st.columns(3)
    with pc1:
        pt1 = st.selectbox("Time 1", TEAM_NAMES, index=0, key="pt1")
    with pc2:
        pt2 = st.selectbox("Time 2", TEAM_NAMES, index=8, key="pt2")
    with pc3:
        phome_opts = [pt1, pt2, "Neutro"]
        phome = st.selectbox("Mando jogo 1", phome_opts, key="phome")

    n_sim = st.slider("Nº de simulações (Monte Carlo)", 1000, 50000, 10000, step=1000)

    if st.button("▶  Simular série", type="primary"):
        with st.spinner("Simulando..."):
            result = calc_win_prob(pt1, pt2, phome if phome != "Neutro" else "Neutro", n_sim)

        st.divider()

        # Big probability display
        prob1, prob2 = result["prob_t1"], result["prob_t2"]
        pcol1, pcol2 = st.columns(2)
        with pcol1:
            st.markdown(f"""
            <div style='text-align:center; padding:1.5rem; background:#1a1a2e; border-radius:12px; border:1px solid {TEAMS[pt1]['color']}'>
                <p style='color:#8888aa;font-size:13px;margin:0'>Probabilidade de vencer a série</p>
                <p style='color:{TEAMS[pt1]['color']};font-size:3rem;font-weight:800;margin:0.3rem 0'>{prob1}%</p>
                <p style='color:#fff;font-size:1.1rem;font-weight:600;margin:0'>{pt1}</p>
            </div>""", unsafe_allow_html=True)
        with pcol2:
            st.markdown(f"""
            <div style='text-align:center; padding:1.5rem; background:#1a1a2e; border-radius:12px; border:1px solid {TEAMS[pt2]['color']}'>
                <p style='color:#8888aa;font-size:13px;margin:0'>Probabilidade de vencer a série</p>
                <p style='color:{TEAMS[pt2]['color']};font-size:3rem;font-weight:800;margin:0.3rem 0'>{prob2}%</p>
                <p style='color:#fff;font-size:1.1rem;font-weight:600;margin:0'>{pt2}</p>
            </div>""", unsafe_allow_html=True)

        # Fatores
        st.markdown("<p class='section-title'>Fatores da simulação</p>", unsafe_allow_html=True)
        fc1, fc2, fc3, fc4 = st.columns(4)
        fc1.metric("Diferença Net Rtg", f"{result['net_diff']:+.2f}")
        fc2.metric("Bônus mando",        f"{result['home_bonus']:+.1f}")
        fc3.metric("Bônus descanso",     f"{result['rest_bonus']:+.1f}")
        fc4.metric("Penalidade lesões",  f"{result['injury_pen']:+.1f}")

        # Series length
        st.markdown("<p class='section-title'>Distribuição provável de duração da série</p>", unsafe_allow_html=True)
        st.plotly_chart(series_length_chart(result["length_dist"], pt1, pt2), use_container_width=True)

        # Game-by-game prob
        st.markdown("<p class='section-title'>Probabilidade por jogo (base)</p>", unsafe_allow_html=True)
        gp = result["game_prob_t1"]
        games_data = []
        w1, w2 = 0, 0
        for g in range(1, 8):
            home_g = pt1 if g % 2 == 1 else pt2
            adj = gp + (3.5 if home_g == pt1 else -3.5) * 0.15
            games_data.append({"Jogo": f"G{g}", "% vitória " + TEAMS[pt1]["abbr"]: round(min(max(adj, 5), 95), 1), "Mando": home_g})

        gdf = pd.DataFrame(games_data)
        st.dataframe(gdf, use_container_width=True, hide_index=True)

        st.info("💡 Dica para vídeo: grave a tela nesse momento com os cards de probabilidade em destaque — é o frame mais visual da análise.")

# Footer
st.divider()
st.markdown("<p style='color:#444;font-size:12px;text-align:center'>Dados: mock stats para demonstração. Conecte nba_api para dados reais em tempo real.</p>", unsafe_allow_html=True)
