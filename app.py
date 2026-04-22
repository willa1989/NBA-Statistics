import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import date

st.set_page_config(
    page_title="NBA Playoffs 2026 Analyzer",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .block-container { padding-top: 1rem; padding-bottom: 2rem; max-width: 1200px; }
    div[data-testid="metric-container"] {
        background: #1a1a2e; border: 1px solid #16213e;
        border-radius: 12px; padding: 1rem 1.2rem;
    }
    div[data-testid="metric-container"] label { color: #8888aa !important; font-size: 12px; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        font-size: 1.8rem; font-weight: 700; color: #ffffff;
    }
    .team-header { font-size: 1.4rem; font-weight: 700; margin-bottom: 0.2rem; color: #ffffff; }
    .section-title {
        font-size: 1rem; font-weight: 600; color: #8888aa;
        text-transform: uppercase; letter-spacing: 0.08em; margin: 1.5rem 0 0.8rem;
    }
    .stTabs [data-baseweb="tab"] { color: #8888aa; }
    .stTabs [aria-selected="true"] { color: #4fa8ff; }
    .stTabs [data-baseweb="tab-highlight"] { background-color: #4fa8ff; }
    hr { border-color: #1e1e3a; }
</style>
""", unsafe_allow_html=True)

# ── Playoffs 2026 — times classificados ───────────────────────────────────────
TEAMS = {
    "Detroit Pistons":        {"color": "#C8102E", "conf": "Leste", "seed": 1, "abbr": "DET"},
    "Boston Celtics":         {"color": "#007A33", "conf": "Leste", "seed": 2, "abbr": "BOS"},
    "New York Knicks":        {"color": "#F58426", "conf": "Leste", "seed": 3, "abbr": "NYK"},
    "Cleveland Cavaliers":    {"color": "#860038", "conf": "Leste", "seed": 4, "abbr": "CLE"},
    "Toronto Raptors":        {"color": "#CE1141", "conf": "Leste", "seed": 5, "abbr": "TOR"},
    "Atlanta Hawks":          {"color": "#E03A3E", "conf": "Leste", "seed": 6, "abbr": "ATL"},
    "Philadelphia 76ers":     {"color": "#006BB6", "conf": "Leste", "seed": 7, "abbr": "PHI"},
    "Orlando Magic":          {"color": "#0077C0", "conf": "Leste", "seed": 8, "abbr": "ORL"},
    "Oklahoma City Thunder":  {"color": "#007AC1", "conf": "Oeste", "seed": 1, "abbr": "OKC"},
    "San Antonio Spurs":      {"color": "#C4CED4", "conf": "Oeste", "seed": 2, "abbr": "SAS"},
    "Denver Nuggets":         {"color": "#4FA8FF", "conf": "Oeste", "seed": 3, "abbr": "DEN"},
    "Los Angeles Lakers":     {"color": "#552583", "conf": "Oeste", "seed": 4, "abbr": "LAL"},
    "Houston Rockets":        {"color": "#CE1141", "conf": "Oeste", "seed": 5, "abbr": "HOU"},
    "Minnesota Timberwolves": {"color": "#0C2340", "conf": "Oeste", "seed": 6, "abbr": "MIN"},
    "Portland Trail Blazers": {"color": "#E03A3E", "conf": "Oeste", "seed": 7, "abbr": "POR"},
    "Phoenix Suns":           {"color": "#E56020", "conf": "Oeste", "seed": 8, "abbr": "PHX"},
}

SERIES = [
    {"t1": "Detroit Pistons",       "t2": "Orlando Magic",          "score": "0-1", "conf": "Leste"},
    {"t1": "Boston Celtics",        "t2": "Philadelphia 76ers",     "score": "1-1", "conf": "Leste"},
    {"t1": "New York Knicks",       "t2": "Atlanta Hawks",          "score": "1-1", "conf": "Leste"},
    {"t1": "Cleveland Cavaliers",   "t2": "Toronto Raptors",        "score": "2-0", "conf": "Leste"},
    {"t1": "Oklahoma City Thunder", "t2": "Phoenix Suns",           "score": "1-0", "conf": "Oeste"},
    {"t1": "San Antonio Spurs",     "t2": "Portland Trail Blazers", "score": "1-1", "conf": "Oeste"},
    {"t1": "Denver Nuggets",        "t2": "Minnesota Timberwolves", "score": "1-1", "conf": "Oeste"},
    {"t1": "Los Angeles Lakers",    "t2": "Houston Rockets",        "score": "2-0", "conf": "Oeste"},
]

TEAM_NAMES = list(TEAMS.keys())

MOCK_STATS = {
    "Detroit Pistons":        {"off_rtg": 117.2, "def_rtg": 109.8, "net_rtg":  7.4, "pace":  99.8, "ts_pct": 57.8, "reb_pct": 52.1, "ast_ratio": 19.2, "tov_ratio": 12.4, "three_pct": 37.1, "clutch_net":  5.8, "rest_days": 2, "injuries": 1, "wins": 60, "losses": 22},
    "Boston Celtics":         {"off_rtg": 120.4, "def_rtg": 110.1, "net_rtg": 10.3, "pace":  97.2, "ts_pct": 59.8, "reb_pct": 51.4, "ast_ratio": 21.8, "tov_ratio": 11.9, "three_pct": 39.4, "clutch_net":  8.2, "rest_days": 2, "injuries": 1, "wins": 56, "losses": 26},
    "New York Knicks":        {"off_rtg": 116.8, "def_rtg": 111.6, "net_rtg":  5.2, "pace":  96.1, "ts_pct": 57.2, "reb_pct": 51.8, "ast_ratio": 18.4, "tov_ratio": 13.1, "three_pct": 36.5, "clutch_net":  4.9, "rest_days": 2, "injuries": 0, "wins": 52, "losses": 30},
    "Cleveland Cavaliers":    {"off_rtg": 119.6, "def_rtg": 108.4, "net_rtg": 11.2, "pace":  98.4, "ts_pct": 59.1, "reb_pct": 53.2, "ast_ratio": 20.6, "tov_ratio": 11.6, "three_pct": 38.2, "clutch_net":  9.4, "rest_days": 3, "injuries": 0, "wins": 58, "losses": 24},
    "Toronto Raptors":        {"off_rtg": 114.2, "def_rtg": 113.8, "net_rtg":  0.4, "pace": 100.1, "ts_pct": 55.9, "reb_pct": 50.1, "ast_ratio": 19.8, "tov_ratio": 14.2, "three_pct": 35.8, "clutch_net":  1.2, "rest_days": 1, "injuries": 2, "wins": 44, "losses": 38},
    "Atlanta Hawks":          {"off_rtg": 116.3, "def_rtg": 114.7, "net_rtg":  1.6, "pace": 101.4, "ts_pct": 56.8, "reb_pct": 50.4, "ast_ratio": 20.1, "tov_ratio": 14.8, "three_pct": 36.1, "clutch_net":  2.1, "rest_days": 2, "injuries": 1, "wins": 46, "losses": 36},
    "Philadelphia 76ers":     {"off_rtg": 114.8, "def_rtg": 113.2, "net_rtg":  1.6, "pace":  96.8, "ts_pct": 56.4, "reb_pct": 51.1, "ast_ratio": 17.9, "tov_ratio": 13.6, "three_pct": 35.4, "clutch_net":  1.8, "rest_days": 2, "injuries": 3, "wins": 44, "losses": 38},
    "Orlando Magic":          {"off_rtg": 115.4, "def_rtg": 110.8, "net_rtg":  4.6, "pace":  97.6, "ts_pct": 56.1, "reb_pct": 52.8, "ast_ratio": 17.6, "tov_ratio": 12.8, "three_pct": 35.9, "clutch_net":  3.4, "rest_days": 1, "injuries": 1, "wins": 47, "losses": 35},
    "Oklahoma City Thunder":  {"off_rtg": 122.8, "def_rtg": 108.1, "net_rtg": 14.7, "pace":  99.2, "ts_pct": 60.4, "reb_pct": 52.9, "ast_ratio": 22.1, "tov_ratio": 11.2, "three_pct": 38.8, "clutch_net": 12.4, "rest_days": 2, "injuries": 0, "wins": 65, "losses": 17},
    "San Antonio Spurs":      {"off_rtg": 119.8, "def_rtg": 102.8, "net_rtg": 17.0, "pace":  98.6, "ts_pct": 59.2, "reb_pct": 51.6, "ast_ratio": 20.8, "tov_ratio": 12.1, "three_pct": 37.6, "clutch_net":  9.8, "rest_days": 2, "injuries": 0, "wins": 62, "losses": 20},
    "Denver Nuggets":         {"off_rtg": 120.1, "def_rtg": 111.4, "net_rtg":  8.7, "pace": 101.8, "ts_pct": 59.4, "reb_pct": 51.8, "ast_ratio": 23.6, "tov_ratio": 12.6, "three_pct": 37.8, "clutch_net":  7.6, "rest_days": 2, "injuries": 1, "wins": 55, "losses": 27},
    "Los Angeles Lakers":     {"off_rtg": 116.4, "def_rtg": 111.2, "net_rtg":  5.2, "pace":  98.4, "ts_pct": 57.6, "reb_pct": 50.6, "ast_ratio": 19.4, "tov_ratio": 13.8, "three_pct": 36.4, "clutch_net":  4.2, "rest_days": 2, "injuries": 2, "wins": 50, "losses": 32},
    "Houston Rockets":        {"off_rtg": 113.8, "def_rtg": 113.2, "net_rtg":  0.6, "pace":  94.8, "ts_pct": 55.6, "reb_pct": 50.8, "ast_ratio": 17.2, "tov_ratio": 13.4, "three_pct": 34.8, "clutch_net":  0.8, "rest_days": 1, "injuries": 1, "wins": 43, "losses": 39},
    "Minnesota Timberwolves": {"off_rtg": 115.8, "def_rtg": 110.4, "net_rtg":  5.4, "pace": 100.2, "ts_pct": 57.1, "reb_pct": 52.6, "ast_ratio": 18.8, "tov_ratio": 13.0, "three_pct": 36.9, "clutch_net":  4.6, "rest_days": 2, "injuries": 1, "wins": 49, "losses": 33},
    "Portland Trail Blazers": {"off_rtg": 116.1, "def_rtg": 113.6, "net_rtg":  2.5, "pace": 101.1, "ts_pct": 56.6, "reb_pct": 50.2, "ast_ratio": 20.4, "tov_ratio": 14.4, "three_pct": 36.8, "clutch_net":  2.8, "rest_days": 2, "injuries": 0, "wins": 45, "losses": 37},
    "Phoenix Suns":           {"off_rtg": 114.4, "def_rtg": 114.8, "net_rtg": -0.4, "pace": 100.4, "ts_pct": 56.2, "reb_pct": 49.8, "ast_ratio": 18.6, "tov_ratio": 14.6, "three_pct": 35.6, "clutch_net":  0.4, "rest_days": 1, "injuries": 2, "wins": 42, "losses": 40},
}

PLAYERS = {
    "Oklahoma City Thunder": [
        {"nome": "Shai Gilgeous-Alexander", "pos": "PG", "pts": 32.4, "reb": 5.2, "ast": 6.8, "fg_pct": 51.2, "three_pct": 38.4, "ts_pct": 63.1, "per": 31.2, "obs": "MVP favorito. Lider em clutch points da liga (175 pts em situacoes clutch)."},
        {"nome": "Jalen Williams",           "pos": "SG", "pts": 23.1, "reb": 4.8, "ast": 5.4, "fg_pct": 49.8, "three_pct": 36.9, "ts_pct": 60.2, "per": 22.4, "obs": "Dupla letal com SGA. Scorer de alto volume."},
        {"nome": "Chet Holmgren",            "pos": "C",  "pts": 18.4, "reb": 8.1, "ast": 2.6, "fg_pct": 52.1, "three_pct": 37.8, "ts_pct": 61.8, "per": 20.1, "obs": "Bloqueador de elite. Ancora defensiva do Thunder."},
    ],
    "San Antonio Spurs": [
        {"nome": "Victor Wembanyama",  "pos": "C",  "pts": 25.0, "reb": 11.5, "ast": 3.8, "fg_pct": 48.6, "three_pct": 34.2, "ts_pct": 59.4, "per": 28.6, "obs": "DPOY unanime. Net rating +17 com ele em quadra. Apenas 22 anos."},
        {"nome": "Kevin Durant",       "pos": "SF", "pts": 27.9, "reb": 4.5,  "ast": 5.7, "fg_pct": 52.4, "three_pct": 40.1, "ts_pct": 62.8, "per": 26.8, "obs": "MVP contender aos 37 anos. Lider em pontos no 4T."},
        {"nome": "Devin Booker",       "pos": "SG", "pts": 24.6, "reb": 4.2,  "ast": 6.1, "fg_pct": 47.9, "three_pct": 37.4, "ts_pct": 60.1, "per": 23.1, "obs": "Scorer de elite nos momentos decisivos."},
    ],
    "Denver Nuggets": [
        {"nome": "Nikola Jokic",    "pos": "C",  "pts": 27.7, "reb": 12.9, "ast": 10.7, "fg_pct": 56.8, "three_pct": 35.6, "ts_pct": 64.4, "per": 34.1, "obs": "1o jogador a liderar NBA em rebotes E assistencias na mesma temporada."},
        {"nome": "Jamal Murray",    "pos": "PG", "pts": 21.4, "reb": 4.1,  "ast": 6.8,  "fg_pct": 48.2, "three_pct": 38.1, "ts_pct": 59.6, "per": 20.8, "obs": "Playoff Murray. Historicamente destruidor nos playoffs."},
        {"nome": "Aaron Gordon",    "pos": "PF", "pts": 14.2, "reb": 7.8,  "ast": 3.4,  "fg_pct": 54.1, "three_pct": 36.2, "ts_pct": 59.8, "per": 17.4, "obs": "+19.8 net rtg quando joga com Jokic. Vital para o DEN."},
    ],
    "Cleveland Cavaliers": [
        {"nome": "Donovan Mitchell", "pos": "SG", "pts": 28.3, "reb": 4.4, "ast": 5.2, "fg_pct": 48.9, "three_pct": 37.8, "ts_pct": 60.8, "per": 25.6, "obs": "All-Star toda a decada. Top scorer no 4T da liga."},
        {"nome": "James Harden",     "pos": "PG", "pts": 18.6, "reb": 4.8, "ast": 8.4, "fg_pct": 44.2, "three_pct": 36.1, "ts_pct": 58.4, "per": 19.2, "obs": "Adquirido no trade deadline. Experiencia crucial em playoffs."},
        {"nome": "Evan Mobley",      "pos": "C",  "pts": 18.1, "reb": 9.4, "ast": 2.8, "fg_pct": 54.6, "three_pct": 33.8, "ts_pct": 60.2, "per": 20.4, "obs": "Defensor elite. Candidato ao DPOY."},
    ],
    "Boston Celtics": [
        {"nome": "Jaylen Brown",     "pos": "SF", "pts": 23.9, "reb": 5.5, "ast": 9.9, "fg_pct": 46.8, "three_pct": 36.4, "ts_pct": 58.6, "per": 22.8, "obs": "MVP contender. Career-high em todos os stats com Tatum machucado."},
        {"nome": "Jayson Tatum",     "pos": "SF", "pts": 18.4, "reb": 7.2, "ast": 4.8, "fg_pct": 44.1, "three_pct": 34.6, "ts_pct": 56.8, "per": 19.6, "obs": "Voltou de ruptura no Aquiles. Ainda se ajustando ao ritmo."},
        {"nome": "Payton Pritchard", "pos": "PG", "pts": 14.8, "reb": 2.9, "ast": 4.1, "fg_pct": 44.6, "three_pct": 39.8, "ts_pct": 60.4, "per": 15.2, "obs": "Shooter volatil — define o resultado das series pelo seu desempenho."},
    ],
    "Detroit Pistons": [
        {"nome": "Cade Cunningham", "pos": "PG", "pts": 24.8, "reb": 5.6, "ast": 8.2, "fg_pct": 46.4, "three_pct": 35.8, "ts_pct": 58.9, "per": 22.6, "obs": "Star em ascensao. Liderou DET a 60 vitorias na temporada."},
        {"nome": "Jalen Duren",     "pos": "C",  "pts": 14.2, "reb": 11.8, "ast": 2.1, "fg_pct": 58.4, "three_pct": 0.0,  "ts_pct": 60.6, "per": 19.8, "obs": "Dominante no garrafao. Melhor em rebotes ofensivos do time."},
        {"nome": "Ausar Thompson",  "pos": "SF", "pts": 16.4, "reb": 6.8,  "ast": 3.2, "fg_pct": 48.2, "three_pct": 34.4, "ts_pct": 57.4, "per": 17.2, "obs": "Atletismo explosivo. Perigo nos cortes para a cesta."},
    ],
    "Los Angeles Lakers": [
        {"nome": "LeBron James",    "pos": "SF", "pts": 22.4, "reb": 7.8,  "ast": 8.1, "fg_pct": 50.2, "three_pct": 36.8, "ts_pct": 60.4, "per": 24.2, "obs": "41 anos. Voltou como armador principal apos lesoes de Doncic e Reaves."},
        {"nome": "Anthony Davis",   "pos": "C",  "pts": 24.6, "reb": 12.4, "ast": 3.1, "fg_pct": 54.8, "three_pct": 28.4, "ts_pct": 60.8, "per": 27.4, "obs": "Dominante quando saudavel. Pillar ofensivo e defensivo do LAL."},
        {"nome": "Austin Reaves",   "pos": "SG", "pts": 16.8, "reb": 4.2,  "ast": 5.4, "fg_pct": 46.8, "three_pct": 39.4, "ts_pct": 60.2, "per": 17.8, "obs": "Lesionado. Situacao incerta para os playoffs."},
    ],
    "New York Knicks": [
        {"nome": "Jalen Brunson",        "pos": "PG", "pts": 26.0, "reb": 3.9,  "ast": 7.0, "fg_pct": 47.4, "three_pct": 37.2, "ts_pct": 59.8, "per": 23.4, "obs": "29.9 pts de media em playoffs com NYK. Clutch absoluto."},
        {"nome": "OG Anunoby",           "pos": "SF", "pts": 17.2, "reb": 5.8,  "ast": 2.4, "fg_pct": 48.8, "three_pct": 38.6, "ts_pct": 59.4, "per": 18.6, "obs": "Defensor versatil. Guarda o melhor atacante adversario."},
        {"nome": "Karl-Anthony Towns",   "pos": "C",  "pts": 22.1, "reb": 10.2, "ast": 3.8, "fg_pct": 50.4, "three_pct": 39.8, "ts_pct": 61.2, "per": 22.8, "obs": "Center com tiro de 3. Matchup dificil para qualquer time."},
    ],
    "Orlando Magic": [
        {"nome": "Paolo Banchero",       "pos": "PF", "pts": 22.8, "reb": 6.8, "ast": 4.2, "fg_pct": 47.6, "three_pct": 33.4, "ts_pct": 57.8, "per": 21.4, "obs": "Franquia do Magic. Surpreendeu no G1 contra Detroit."},
        {"nome": "Franz Wagner",         "pos": "SF", "pts": 20.4, "reb": 5.1, "ast": 4.8, "fg_pct": 48.2, "three_pct": 36.8, "ts_pct": 58.6, "per": 19.8, "obs": "Completo. Criador de jogadas e bom defensor."},
        {"nome": "Wendell Carter Jr.",   "pos": "C",  "pts": 13.4, "reb": 9.8, "ast": 2.6, "fg_pct": 54.2, "three_pct": 32.4, "ts_pct": 58.4, "per": 17.6, "obs": "Ancora defensiva. Reboteiro solido do Magic."},
    ],
    "Philadelphia 76ers": [
        {"nome": "Tyrese Maxey",   "pos": "PG", "pts": 24.8, "reb": 3.8, "ast": 6.4, "fg_pct": 46.2, "three_pct": 36.8, "ts_pct": 59.4, "per": 21.8, "obs": "Liderando time sem Embiid (apendicite). Surpreendeu BOS no G2."},
        {"nome": "VJ Edgecombe",   "pos": "SG", "pts": 16.0, "reb": 5.6, "ast": 3.2, "fg_pct": 47.8, "three_pct": 35.2, "ts_pct": 58.8, "per": 17.4, "obs": "Rookie revelacao. 30-10 no G2 contra Boston. ROY contender."},
        {"nome": "Paul George",    "pos": "SF", "pts": 18.4, "reb": 5.2, "ast": 4.1, "fg_pct": 45.8, "three_pct": 37.4, "ts_pct": 57.8, "per": 18.2, "obs": "Veterano experiente. Trunfo da PHI em series longas."},
    ],
    "Atlanta Hawks": [
        {"nome": "Nickeil Alexander-Walker", "pos": "PG", "pts": 20.8, "reb": 4.2, "ast": 5.8, "fg_pct": 46.4, "three_pct": 37.2, "ts_pct": 58.6, "per": 19.6, "obs": "MIP contender. Career-high em todos os stats principais."},
        {"nome": "Jalen Johnson",            "pos": "PF", "pts": 19.6, "reb": 8.4, "ast": 4.8, "fg_pct": 50.2, "three_pct": 34.8, "ts_pct": 59.4, "per": 20.8, "obs": "Versatil. Um dos 3 jogadores com mais triplos-duplos na liga."},
        {"nome": "Clint Capela",             "pos": "C",  "pts": 12.4, "reb": 11.2, "ast": 1.4, "fg_pct": 60.4, "three_pct": 0.0, "ts_pct": 62.8, "per": 16.4, "obs": "Reboteiro veterano. Pick-and-roll com NAW como arma ofensiva."},
    ],
    "Toronto Raptors": [
        {"nome": "Scottie Barnes", "pos": "SF", "pts": 22.4, "reb": 8.6, "ast": 5.8, "fg_pct": 48.4, "three_pct": 34.8, "ts_pct": 58.8, "per": 21.6, "obs": "Star do futuro. Franquia do TOR em desenvolvimento."},
        {"nome": "RJ Barrett",     "pos": "SG", "pts": 19.8, "reb": 5.4, "ast": 4.2, "fg_pct": 46.8, "three_pct": 35.8, "ts_pct": 57.6, "per": 18.4, "obs": "Scorer consistente. Peca chave do ataque dos Raptors."},
        {"nome": "Jakob Poeltl",   "pos": "C",  "pts": 14.2, "reb": 10.4, "ast": 3.2, "fg_pct": 58.6, "three_pct": 0.0, "ts_pct": 62.4, "per": 18.8, "obs": "Defensor elite. Ancora do garrafao dos Raptors."},
    ],
    "Houston Rockets": [
        {"nome": "Alperen Sengun", "pos": "C",  "pts": 21.4, "reb": 9.8, "ast": 4.6, "fg_pct": 52.4, "three_pct": 28.4, "ts_pct": 59.8, "per": 22.4, "obs": "Star emergente. Jogo de costas unico na liga."},
        {"nome": "Jalen Green",    "pos": "SG", "pts": 22.8, "reb": 4.2, "ast": 4.6, "fg_pct": 44.8, "three_pct": 35.6, "ts_pct": 57.4, "per": 18.8, "obs": "Atletismo explosivo. Scorer primario do HOU."},
        {"nome": "Fred VanVleet",  "pos": "PG", "pts": 14.8, "reb": 3.6, "ast": 7.4, "fg_pct": 42.4, "three_pct": 36.8, "ts_pct": 55.8, "per": 15.6, "obs": "Veterano lider. Cerebro do ataque dos Rockets."},
    ],
    "Minnesota Timberwolves": [
        {"nome": "Anthony Edwards", "pos": "SG", "pts": 26.4, "reb": 5.6, "ast": 5.2, "fg_pct": 46.8, "three_pct": 36.4, "ts_pct": 58.8, "per": 23.4, "obs": "Face da franquia. Atletismo de elite. Ameaca constante."},
        {"nome": "Julius Randle",   "pos": "PF", "pts": 20.8, "reb": 8.4, "ast": 4.8, "fg_pct": 48.4, "three_pct": 34.6, "ts_pct": 58.6, "per": 20.6, "obs": "Adquirido para ser segunda opcao. Experiente em playoffs."},
        {"nome": "Rudy Gobert",     "pos": "C",  "pts": 12.8, "reb": 12.4, "ast": 1.8, "fg_pct": 62.4, "three_pct": 0.0, "ts_pct": 65.4, "per": 18.8, "obs": "Missao declarada: neutralizar Jokic. Melhor reboteiro do time."},
    ],
    "Portland Trail Blazers": [
        {"nome": "Deni Avdija",         "pos": "SF", "pts": 24.2, "reb": 7.8, "ast": 6.7, "fg_pct": 49.4, "three_pct": 37.8, "ts_pct": 60.4, "per": 23.2, "obs": "MIP contender. Career-highs em pontos e assistencias."},
        {"nome": "Anfernee Simons",     "pos": "PG", "pts": 22.6, "reb": 3.4, "ast": 5.8, "fg_pct": 44.8, "three_pct": 38.4, "ts_pct": 58.6, "per": 19.4, "obs": "Scorer de alto volume. Perigoso no arremesso de media distancia."},
        {"nome": "Robert Williams III", "pos": "C",  "pts": 10.4, "reb": 8.4, "ast": 1.8, "fg_pct": 60.4, "three_pct": 0.0, "ts_pct": 62.4, "per": 15.8, "obs": "Voltou das lesoes. Defensor elite quando saudavel."},
    ],
    "Phoenix Suns": [
        {"nome": "Bradley Beal",   "pos": "SG", "pts": 20.4, "reb": 4.8, "ast": 5.4, "fg_pct": 46.2, "three_pct": 35.8, "ts_pct": 58.4, "per": 18.6, "obs": "Producao aceitavel na temporada. Lider do ataque dos Suns."},
        {"nome": "Grayson Allen",  "pos": "SG", "pts": 14.2, "reb": 3.6, "ast": 2.8, "fg_pct": 46.8, "three_pct": 41.2, "ts_pct": 61.4, "per": 14.8, "obs": "Especialista em 3P. Perigosíssimo se deixado aberto."},
        {"nome": "Nick Richards",  "pos": "C",  "pts": 12.8, "reb": 9.6, "ast": 1.4, "fg_pct": 56.4, "three_pct": 0.0,  "ts_pct": 58.6, "per": 15.4, "obs": "Center versatil. Construindo identidade na liga."},
    ],
}


def hex_to_rgba(hex_color, alpha=0.25):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def calc_win_prob(t1, t2, home, n_sim=10000):
    s1, s2 = MOCK_STATS[t1], MOCK_STATS[t2]
    net_diff = s1["net_rtg"] - s2["net_rtg"]
    home_bonus = 3.5 if home == t1 else (-3.5 if home == t2 else 0)
    rest_bonus = (s1["rest_days"] - s2["rest_days"]) * 0.4
    injury_pen = (s2["injuries"] - s1["injuries"]) * 1.2
    clutch_bonus = (s1["clutch_net"] - s2["clutch_net"]) * 0.15
    adjusted_diff = net_diff + home_bonus + rest_bonus + injury_pen + clutch_bonus
    base_prob = 1 / (1 + np.exp(-adjusted_diff * 0.15))
    np.random.seed(42)
    t1_wins = 0
    for _ in range(n_sim):
        w1, w2 = 0, 0
        while w1 < 4 and w2 < 4:
            ha = 3.5 if (w1 + w2) % 2 == 0 else -3.5
            p = 1 / (1 + np.exp(-(adjusted_diff + ha) * 0.15))
            if np.random.random() < min(max(p + np.random.normal(0, 0.05), 0.05), 0.95):
                w1 += 1
            else:
                w2 += 1
        if w1 == 4:
            t1_wins += 1
    series_prob = t1_wins / n_sim

    def sim_length(p, n=n_sim):
        lengths = {4: 0, 5: 0, 6: 0, 7: 0}
        for _ in range(n):
            w1, w2 = 0, 0
            while w1 < 4 and w2 < 4:
                if np.random.random() < p:
                    w1 += 1
                else:
                    w2 += 1
            lengths[w1 + w2] += 1
        return {k: round(v / n * 100, 1) for k, v in lengths.items()}

    return {
        "prob_t1": round(series_prob * 100, 1),
        "prob_t2": round((1 - series_prob) * 100, 1),
        "game_prob_t1": round(base_prob * 100, 1),
        "net_diff": round(adjusted_diff, 2),
        "home_bonus": round(home_bonus, 1),
        "rest_bonus": round(rest_bonus, 1),
        "injury_pen": round(injury_pen, 1),
        "length_dist": sim_length(base_prob),
    }


def radar_chart(t1, t2):
    categories = ["Ataque", "Defesa (inv)", "3P%", "Rebotes%", "Assist Ratio", "Clutch Net"]
    s1, s2 = MOCK_STATS[t1], MOCK_STATS[t2]

    def norm(v, lo, hi):
        return round(max(0, min((v - lo) / (hi - lo) * 10, 10)), 2)

    def vals(s):
        return [norm(s["off_rtg"], 110, 125), norm(130 - s["def_rtg"], 110, 28),
                norm(s["three_pct"], 33, 42), norm(s["reb_pct"], 48, 55),
                norm(s["ast_ratio"], 15, 25), norm(s["clutch_net"], -3, 15)]

    v1, v2 = vals(s1), vals(s2)
    fig = go.Figure()
    for vl, name, color in [(v1, t1, TEAMS[t1]["color"]), (v2, t2, TEAMS[t2]["color"])]:
        vc = vl + [vl[0]]
        fig.add_trace(go.Scatterpolar(
            r=vc, theta=categories + [categories[0]], fill="toself", name=name,
            line=dict(color=color, width=2), fillcolor=hex_to_rgba(color, 0.25),
        ))
    fig.update_layout(
        polar=dict(bgcolor="#0a0a0a",
                   radialaxis=dict(visible=True, range=[0, 10], gridcolor="#1e1e3a", color="#444"),
                   angularaxis=dict(gridcolor="#1e1e3a", color="#888")),
        paper_bgcolor="#0a0a0a", plot_bgcolor="#0a0a0a",
        showlegend=True, legend=dict(font=dict(color="#ccc"), bgcolor="#0a0a0a"),
        margin=dict(t=40, b=40, l=60, r=60), height=400,
    )
    return fig


def bar_compare(t1, t2):
    s1, s2 = MOCK_STATS[t1], MOCK_STATS[t2]
    metrics = ["Ataque", "Defesa", "Saldo", "3P%", "TS%", "Clutch"]
    v1 = [s1["off_rtg"], s1["def_rtg"], s1["net_rtg"], s1["three_pct"], s1["ts_pct"], s1["clutch_net"]]
    v2 = [s2["off_rtg"], s2["def_rtg"], s2["net_rtg"], s2["three_pct"], s2["ts_pct"], s2["clutch_net"]]
    fig = go.Figure()
    fig.add_trace(go.Bar(name=t1, x=metrics, y=v1, marker_color=TEAMS[t1]["color"], opacity=0.9))
    fig.add_trace(go.Bar(name=t2, x=metrics, y=v2, marker_color=TEAMS[t2]["color"], opacity=0.9))
    fig.update_layout(barmode="group", paper_bgcolor="#0a0a0a", plot_bgcolor="#0a0a0a",
                      font=dict(color="#ccc"), xaxis=dict(gridcolor="#1e1e3a"),
                      yaxis=dict(gridcolor="#1e1e3a"), legend=dict(bgcolor="#0a0a0a"),
                      margin=dict(t=20, b=20, l=40, r=20), height=320)
    return fig


def leaderboard_chart():
    sorted_teams = sorted(MOCK_STATS.items(), key=lambda x: x[1]["net_rtg"], reverse=True)
    fig = go.Figure(go.Bar(
        x=[round(s["net_rtg"], 1) for _, s in sorted_teams],
        y=[TEAMS[t]["abbr"] for t, _ in sorted_teams],
        orientation="h",
        marker_color=[TEAMS[t]["color"] for t, _ in sorted_teams],
        text=[f"{round(s['net_rtg'],1):+.1f}" for _, s in sorted_teams],
        textposition="auto", textfont=dict(color="#fff"),
    ))
    fig.update_layout(paper_bgcolor="#0a0a0a", plot_bgcolor="#0a0a0a",
                      font=dict(color="#ccc"), xaxis=dict(gridcolor="#1e1e3a", title="Net Rating"),
                      yaxis=dict(gridcolor="#1e1e3a"), margin=dict(t=20, b=20, l=50, r=20),
                      height=560, showlegend=False)
    return fig


def series_length_chart(length_dist):
    fig = go.Figure(go.Bar(
        x=[f"Jogo {k}" for k in length_dist.keys()],
        y=list(length_dist.values()),
        marker_color=["#4fa8ff", "#5fb87f", "#f5a623", "#e84040"],
        text=[f"{p:.1f}%" for p in length_dist.values()],
        textposition="outside", textfont=dict(color="#ccc"),
    ))
    fig.update_layout(paper_bgcolor="#0a0a0a", plot_bgcolor="#0a0a0a",
                      font=dict(color="#ccc"), yaxis=dict(gridcolor="#1e1e3a", title="Probabilidade (%)"),
                      margin=dict(t=20, b=20, l=40, r=20), height=280, showlegend=False)
    return fig


def player_chart(team):
    players = PLAYERS.get(team, [])
    if not players:
        return None
    names = [p["nome"].split()[-1] for p in players]
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Pontos",       x=names, y=[p["pts"] for p in players], marker_color=TEAMS[team]["color"], opacity=0.9))
    fig.add_trace(go.Bar(name="Rebotes",      x=names, y=[p["reb"] for p in players], marker_color="#5fb87f", opacity=0.8))
    fig.add_trace(go.Bar(name="Assistencias", x=names, y=[p["ast"] for p in players], marker_color="#f5a623", opacity=0.8))
    fig.update_layout(barmode="group", paper_bgcolor="#0a0a0a", plot_bgcolor="#0a0a0a",
                      font=dict(color="#ccc"), xaxis=dict(gridcolor="#1e1e3a"),
                      yaxis=dict(gridcolor="#1e1e3a"), legend=dict(bgcolor="#0a0a0a"),
                      margin=dict(t=20, b=20, l=40, r=20), height=280)
    return fig


# ══════════════════════════════════════════════════════════════════════════════
st.markdown("# 🏀 NBA Playoffs 2026 Analyzer")
st.markdown(
    f"<p style='color:#8888aa;margin-top:-0.8rem'>Dados atualizados em {date.today().strftime('%d/%m/%Y')} "
    f"· 1ª Rodada em andamento · 16 times classificados</p>",
    unsafe_allow_html=True,
)
st.divider()

tabs = st.tabs(["🗓️  Bracket & Séries", "⚔️  Confronto direto", "🏅  Jogadores", "📊  Ranking geral", "🎯  Simulação de série"])

# TAB 0 ── Bracket
with tabs[0]:
    st.markdown("<p class='section-title'>Confrontos 1ª rodada — 22/04/2026</p>", unsafe_allow_html=True)
    col_e, col_o = st.columns(2)
    for col, conf in [(col_e, "Leste"), (col_o, "Oeste")]:
        with col:
            st.markdown(f"**Conferência {conf}**")
            for s in [x for x in SERIES if x["conf"] == conf]:
                c1 = TEAMS[s["t1"]]["color"]
                c2 = TEAMS[s["t2"]]["color"]
                sd1, sd2 = TEAMS[s["t1"]]["seed"], TEAMS[s["t2"]]["seed"]
                st.markdown(
                    f"<div style='background:#1a1a2e;border-radius:10px;padding:10px 14px;margin:6px 0;"
                    f"border-left:4px solid {c1}'>"
                    f"<span style='color:{c1};font-weight:600'>({sd1}) {s['t1']}</span>"
                    f" <span style='color:#8888aa;font-size:13px'>vs</span> "
                    f"<span style='color:{c2};font-weight:600'>({sd2}) {s['t2']}</span>"
                    f"&nbsp;&nbsp;<span style='background:#0e2240;color:#4fa8ff;padding:2px 10px;"
                    f"border-radius:6px;font-size:13px;font-weight:700'>{s['score']}</span>"
                    f"</div>", unsafe_allow_html=True)

# TAB 1 ── Confronto direto
with tabs[1]:
    c1s, c2s, c3s = st.columns(3)
    with c1s: t1 = st.selectbox("Time 1", TEAM_NAMES, index=0)
    with c2s: t2 = st.selectbox("Time 2", TEAM_NAMES, index=8)
    with c3s: home = st.selectbox("Mando jogo 1", [t1, t2, "Neutro"])
    s1, s2 = MOCK_STATS[t1], MOCK_STATS[t2]
    st.divider()
    col1, col2 = st.columns(2)
    for col, team, stats in [(col1, t1, s1), (col2, t2, s2)]:
        with col:
            tc = TEAMS[team]["color"]; ts = TEAMS[team]["seed"]; tf = TEAMS[team]["conf"]
            st.markdown(f"<p class='team-header' style='color:{tc}'>{team} — #{ts} {tf}</p>", unsafe_allow_html=True)
            mc1, mc2, mc3, mc4 = st.columns(4)
            mc1.metric("Ataque", f"{stats['off_rtg']:.1f}")
            mc2.metric("Defesa", f"{stats['def_rtg']:.1f}")
            mc3.metric("Saldo",  f"{stats['net_rtg']:+.1f}")
            mc4.metric("Clutch", f"{stats['clutch_net']:+.1f}")
    st.markdown("<p class='section-title'>Comparativo de métricas</p>", unsafe_allow_html=True)
    st.plotly_chart(bar_compare(t1, t2), use_container_width=True)
    st.markdown("<p class='section-title'>Radar de performance</p>", unsafe_allow_html=True)
    st.plotly_chart(radar_chart(t1, t2), use_container_width=True)
    st.markdown("<p class='section-title'>Contexto</p>", unsafe_allow_html=True)
    cx1, cx2, cx3, cx4 = st.columns(4)
    cx1.metric(f"Campanha {TEAMS[t1]['abbr']}", f"{s1['wins']}-{s1['losses']}")
    cx2.metric(f"Lesoes {TEAMS[t1]['abbr']}",   f"{s1['injuries']}")
    cx3.metric(f"Campanha {TEAMS[t2]['abbr']}", f"{s2['wins']}-{s2['losses']}")
    cx4.metric(f"Lesoes {TEAMS[t2]['abbr']}",   f"{s2['injuries']}")

# TAB 2 ── Jogadores
with tabs[2]:
    st.markdown("<p class='section-title'>Estatísticas dos jogadores-chave — temporada 2025-26</p>", unsafe_allow_html=True)
    team_sel = st.selectbox("Selecione o time", TEAM_NAMES, key="team_players")
    players = PLAYERS.get(team_sel, [])
    if players:
        fig_p = player_chart(team_sel)
        if fig_p:
            st.plotly_chart(fig_p, use_container_width=True)
        for p in players:
            color = TEAMS[team_sel]["color"]
            st.markdown(
                f"<div style='background:#1a1a2e;border-radius:12px;padding:14px 18px;margin:8px 0;"
                f"border-left:4px solid {color}'>"
                f"<div style='display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px'>"
                f"<div><span style='color:#fff;font-weight:700;font-size:15px'>{p['nome']}</span>"
                f"&nbsp;<span style='background:#0e2240;color:#4fa8ff;padding:2px 8px;border-radius:4px;font-size:11px'>{p['pos']}</span></div>"
                f"<div style='display:flex;gap:14px;color:#ccc;font-size:13px;flex-wrap:wrap'>"
                f"<span><b style='color:{color}'>{p['pts']}</b> pts</span>"
                f"<span><b style='color:#5fb87f'>{p['reb']}</b> reb</span>"
                f"<span><b style='color:#f5a623'>{p['ast']}</b> ast</span>"
                f"<span><b>{p['fg_pct']:.1f}%</b> FG</span>"
                f"<span><b>{p['ts_pct']:.1f}%</b> TS</span>"
                f"<span><b>{p['per']:.1f}</b> PER</span>"
                f"</div></div>"
                f"<p style='color:#8888aa;font-size:12px;margin:6px 0 0'>{p['obs']}</p>"
                f"</div>", unsafe_allow_html=True)
    st.divider()
    st.markdown("<p class='section-title'>Comparar jogadores entre dois times</p>", unsafe_allow_html=True)
    cmp1, cmp2 = st.columns(2)
    with cmp1: team_a = st.selectbox("Time A", TEAM_NAMES, index=0, key="cmp_a")
    with cmp2: team_b = st.selectbox("Time B", TEAM_NAMES, index=8, key="cmp_b")
    rows = []
    for team in [team_a, team_b]:
        for p in PLAYERS.get(team, []):
            rows.append({"Time": TEAMS[team]["abbr"], "Jogador": p["nome"], "Pos": p["pos"],
                         "Pts": p["pts"], "Reb": p["reb"], "Ast": p["ast"],
                         "FG%": p["fg_pct"], "3P%": p["three_pct"], "TS%": p["ts_pct"], "PER": p["per"]})
    if rows:
        df_p = pd.DataFrame(rows)
        st.dataframe(df_p.style.background_gradient(subset=["Pts", "PER"], cmap="YlOrRd"),
                     use_container_width=True, hide_index=True)

# TAB 3 ── Ranking geral
with tabs[3]:
    st.markdown("<p class='section-title'>Net Rating — temporada regular 2025-26</p>", unsafe_allow_html=True)
    st.plotly_chart(leaderboard_chart(), use_container_width=True)
    df = pd.DataFrame([
        {"Time": t, "Conf": TEAMS[t]["conf"], "Seed": TEAMS[t]["seed"],
         "Campanha": f"{s['wins']}-{s['losses']}",
         "Ataque": round(s["off_rtg"], 1), "Defesa": round(s["def_rtg"], 1),
         "Saldo": round(s["net_rtg"], 1), "Ritmo": round(s["pace"], 1),
         "TS%": round(s["ts_pct"], 1), "3P%": round(s["three_pct"], 1),
         "Reb%": round(s["reb_pct"], 1), "Clutch": round(s["clutch_net"], 1),
         "Lesoes": s["injuries"]}
        for t, s in sorted(MOCK_STATS.items(), key=lambda x: x[1]["net_rtg"], reverse=True)
    ])
    st.dataframe(df.style.background_gradient(subset=["Saldo"], cmap="RdYlGn"),
                 use_container_width=True, hide_index=True)

# TAB 4 ── Simulação
with tabs[4]:
    st.markdown("**Configure o confronto e simule a série (Monte Carlo)**")
    pc1, pc2, pc3 = st.columns(3)
    with pc1: pt1 = st.selectbox("Time 1", TEAM_NAMES, index=0, key="pt1")
    with pc2: pt2 = st.selectbox("Time 2", TEAM_NAMES, index=8, key="pt2")
    with pc3: phome = st.selectbox("Mando jogo 1", [pt1, pt2, "Neutro"], key="phome")
    n_sim = st.slider("Nº de simulacoes", 1000, 50000, 10000, step=1000)

    if st.button("▶  Simular série", type="primary"):
        with st.spinner("Simulando..."):
            result = calc_win_prob(pt1, pt2, phome if phome != "Neutro" else "Neutro", n_sim)
        st.divider()
        p1, p2 = result["prob_t1"], result["prob_t2"]
        pcol1, pcol2 = st.columns(2)
        for col, team, prob in [(pcol1, pt1, p1), (pcol2, pt2, p2)]:
            with col:
                color = TEAMS[team]["color"]
                st.markdown(
                    f"<div style='text-align:center;padding:1.5rem;background:#1a1a2e;border-radius:12px;"
                    f"border:2px solid {color}'>"
                    f"<p style='color:#8888aa;font-size:13px;margin:0'>Probabilidade de vencer a série</p>"
                    f"<p style='color:{color};font-size:3rem;font-weight:800;margin:0.3rem 0'>{prob}%</p>"
                    f"<p style='color:#fff;font-size:1.1rem;font-weight:600;margin:0'>{team}</p>"
                    f"</div>", unsafe_allow_html=True)
        st.markdown("<p class='section-title'>Fatores do modelo</p>", unsafe_allow_html=True)
        fc1, fc2, fc3, fc4 = st.columns(4)
        fc1.metric("Diferenca Saldo", f"{result['net_diff']:+.2f}")
        fc2.metric("Bonus mando",     f"{result['home_bonus']:+.1f}")
        fc3.metric("Bonus descanso",  f"{result['rest_bonus']:+.1f}")
        fc4.metric("Fator lesoes",    f"{result['injury_pen']:+.1f}")
        st.markdown("<p class='section-title'>Duração prevista da série</p>", unsafe_allow_html=True)
        st.plotly_chart(series_length_chart(result["length_dist"]), use_container_width=True)
        st.markdown("<p class='section-title'>Probabilidade por jogo</p>", unsafe_allow_html=True)
        gp = result["game_prob_t1"]
        games_data = [{"Jogo": f"G{g}",
                       f"% {TEAMS[pt1]['abbr']}": round(min(max(gp + (3.5 if g % 2 == 1 else -3.5) * 0.15, 5), 95), 1),
                       "Mando": pt1 if g % 2 == 1 else pt2} for g in range(1, 8)]
        st.dataframe(pd.DataFrame(games_data), use_container_width=True, hide_index=True)
        st.info("Dica: grave a tela nos cards de probabilidade — e o frame mais visual para o video.")

st.divider()
st.markdown(
    "<p style='color:#444;font-size:12px;text-align:center'>"
    "Temporada regular 2025-26 | NBA Playoffs 2026 — 1ª rodada | Atualizado 22/04/2026"
    "</p>", unsafe_allow_html=True)
