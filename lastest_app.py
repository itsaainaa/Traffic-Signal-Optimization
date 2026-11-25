# ============================================================
# AHMEDABAD TRAFFIC OPTIMIZATION — INTERACTIVE DASHBOARD (v2)
# ------------------------------------------------------------
# Run with:   streamlit run app_new.py
# Needs:      streamlit, pandas, numpy, plotly
# Files:      Ahmedabad_Traffic_2036_Master_Dataset.csv  (same folder)
#             assets/  (figures extracted from your project report;
#                       optional - the app still works without them)
# ============================================================

from pathlib import Path
import math

import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Ahmedabad Traffic Optimization",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent
ASSETS = BASE_DIR / "assets"
CSV_NAME = "Ahmedabad_Traffic_2036_Master_Dataset.csv"

# ============================================================
# CONSTANTS
# ============================================================
BASE_YEAR, FUTURE_YEAR = 2026, 2036

C_NOW, C_FUT = "#00b8d9", "#7c4dff"      # 2026 / future
C_NS, C_EW = "#2f80ed", "#ff8a3d"        # signal phases
C_OK, C_WARN, C_BAD = "#00c48c", "#ffb020", "#ff4d5e"

TYPES = ["Two-Wheeler", "Car", "Auto-Rickshaw", "Bus",
         "Light Commercial", "Heavy Truck", "Bicycle"]
MIX_COLS = [f"{t} (%)" for t in TYPES]
TYPE_COLORS = ["#00b8d9", "#7c4dff", "#ffb020", "#00c48c",
               "#ff8a3d", "#ff4d5e", "#8892a6"]

# Passenger-car-unit weights (editable in the sidebar, IRC-style defaults)
DEFAULT_PCU = {"Two-Wheeler": 0.5, "Car": 1.0, "Auto-Rickshaw": 1.2,
               "Bus": 2.2, "Light Commercial": 1.4,
               "Heavy Truck": 3.7, "Bicycle": 0.4}

COMP_PRESETS = {
    "Current Vehicle Mix": {},
    "Two-Wheeler Dominant Mix": {"Two-Wheeler": 1.5},
    "Car Dominant Mix": {"Car": 1.5},
    "Public-Transport Shift": {"Bus": 2.0, "Car": 0.8, "Two-Wheeler": 0.85},
    "Custom Mix": None,
}

# Fallback copy of the report results (ISKCON Cross Road) — used only when the
# raw 5-minute Excel file is not next to this script.
ALL_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
CONG_COLORS = {"Low": "#00c48c", "Moderate": "#ffb020", "High": "#ff8a3d", "Severe": "#ff4d5e"}

PERIODS = ["Morning peak", "Midday", "Evening peak", "Late evening", "Night"]
PERIOD_AVG = [5.22, 3.80, 6.47, 2.07, 0.84]            # Graph 1

DAYS = ["Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
PRED = np.array([[5.59, 4.06, 6.67, 2.22, 0.92],
                 [5.52, 4.09, 6.78, 2.17, 0.92],
                 [5.55, 4.05, 6.71, 2.18, 0.91],
                 [5.54, 4.04, 6.71, 2.17, 0.90],
                 [5.51, 4.01, 6.77, 2.17, 0.90],
                 [5.34, 3.88, 6.63, 2.11, 0.86]])
ACT = np.array([[5.44, 4.11, 6.89, 2.11, 0.92],
                [5.61, 3.98, 6.58, 2.22, 0.90],
                [5.51, 3.99, 6.70, 2.14, 0.88],
                [5.39, 3.92, 7.01, 2.17, 0.88],
                [4.47, 3.24, 5.90, 1.78, 0.69],
                [4.54, 3.26, 5.53, 1.84, 0.68]])
EVE_LO = [2.19, 6.48, 6.41, 6.46, 6.43, 5.86]          # 95% band, evening peak
EVE_HI = [11.14, 7.08, 7.02, 6.96, 7.11, 7.39]

WEEK = pd.DataFrame({
    "Day": DAYS,
    "NS Demand": [11.77, 7.38, 7.41, 7.36, 7.59, 7.98],
    "EW Demand": [9.52, 6.78, 6.65, 6.57, 6.66, 6.81],
    "NS Green": [57.91, 56.18, 56.49, 56.56, 56.79, 57.18],
    "EW Green": [52.09, 53.82, 53.51, 53.44, 53.21, 52.82],
    "NS -20%": [54.85, 53.11, 53.42, 53.49, 53.73, 54.11],
    "NS -10%": [56.47, 54.73, 55.04, 55.11, 55.35, 55.73],
    "NS +10%": [59.22, 57.49, 57.80, 57.87, 58.10, 58.49],
    "NS +20%": [60.41, 58.68, 58.99, 59.06, 59.29, 59.68],
})

# ============================================================
# STYLING
# ============================================================
BASE_CSS = """
<style>
footer, [data-testid="stDecoration"], #MainMenu {visibility:hidden;}
[data-testid="stHeader"] {background: transparent;}
.block-container {max-width: 100% !important; padding: 1.2rem 2rem 3rem 2rem !important;}

/* ---------- hero ---------- */
.hero {position:relative; overflow:hidden; border-radius:22px; padding:30px 36px;
  margin-bottom:18px; color:#f4f8ff;
  background: radial-gradient(circle at 85% 20%, rgba(0,229,255,.25), transparent 35%),
              radial-gradient(circle at 10% 90%, rgba(124,77,255,.25), transparent 35%),
              linear-gradient(135deg,#071525,#0c1f3a 60%,#071525);
  border:1px solid rgba(0,220,255,.2); box-shadow:0 8px 40px rgba(0,120,200,.18);}
.hero::before {content:""; position:absolute; top:0; left:0; width:100%; height:3px;
  background:linear-gradient(90deg,#00e5ff,#7c4dff,#00e5ff);}
.hero .eyebrow {font-size:11px; letter-spacing:4px; color:#7fb7d0; font-weight:600;}
.hero h1 {margin:8px 0 6px 0; font-size:clamp(26px,3.4vw,44px); font-weight:800; line-height:1.05; color:#f4f8ff;}
.hero h1 span {color:#00e5ff; text-shadow:0 0 22px rgba(0,229,255,.35);}
.hero p {color:#a9bdd0; margin:0 0 14px 0; font-size:14px; max-width:900px;}
.chip {display:inline-block; margin:0 8px 6px 0; padding:6px 14px; border-radius:999px;
  background:rgba(0,229,255,.08); border:1px solid rgba(0,229,255,.25);
  color:#9fe6f2; font-size:12px; font-weight:600; letter-spacing:.5px;}

/* ---------- KPI cards ---------- */
.kpi {border:1px solid rgba(128,128,128,.25); border-left:5px solid var(--c);
  border-radius:14px; padding:14px 16px; background:rgba(128,128,128,.07); height:100%;}
.kpi-l {font-size:12px; letter-spacing:1px; text-transform:uppercase; opacity:.7; font-weight:600;}
.kpi-v {font-size:30px; font-weight:800; line-height:1.15; margin-top:4px;}
.kpi-s {font-size:12px; opacity:.75; margin-top:2px;}

.verdict {border-radius:18px; padding:20px 22px; position:relative; overflow:hidden;
  border:1px solid rgba(128,128,128,.28); background:linear-gradient(135deg, rgba(128,128,128,.10), rgba(128,128,128,.03));}
.verdict::before {content:""; position:absolute; left:0; top:0; bottom:0; width:6px; background:var(--c);}
.v-badge {display:inline-block; padding:4px 12px; border-radius:999px; font-size:11px; font-weight:800;
  letter-spacing:1.5px; color:#fff; background:var(--c);}
.v-head {font-size:20px; font-weight:800; line-height:1.3; margin:12px 0 10px 0;}
.v-head b {color:var(--c);}
.v-act {border-top:1px dashed rgba(128,128,128,.4); padding-top:10px; font-size:14px; opacity:.9;}
.v-row {display:flex; gap:10px; margin:10px 0;}
.v-pill {flex:1; border-radius:12px; padding:8px 10px; background:rgba(128,128,128,.12); text-align:center;}
.v-pill small {display:block; font-size:10px; letter-spacing:1px; opacity:.65; font-weight:700;}
.v-pill span {font-size:18px; font-weight:800;}
.ins-grid {display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin:6px 0 14px 0;}
@media (max-width:1100px) {.ins-grid {grid-template-columns:repeat(2,1fr);} }
@media (max-width:700px) {.ins-grid {grid-template-columns:1fr;} }
.ins {border-radius:16px; padding:16px 18px; border:1px solid rgba(128,128,128,.25); position:relative;
  background:rgba(128,128,128,.06); transition:transform .15s ease, box-shadow .15s ease; overflow:hidden;}
.ins:hover {transform:translateY(-3px); box-shadow:0 8px 24px rgba(0,0,0,.18);}
.ins::after {content:""; position:absolute; top:0; left:0; right:0; height:4px; background:var(--c);}
.ins-top {display:flex; align-items:center; gap:10px; margin-bottom:6px;}
.ins-ic {width:34px; height:34px; border-radius:10px; display:flex; align-items:center; justify-content:center;
  font-size:18px; background:color-mix(in srgb, var(--c) 18%, transparent);}
.ins-tag {font-size:11px; letter-spacing:1.5px; font-weight:800; opacity:.7;}
.ins-big {font-size:30px; font-weight:900; line-height:1.1; color:var(--c);}
.ins-big small {font-size:14px; font-weight:600; opacity:.6; margin-left:6px; color:inherit;}
.ins-txt {font-size:13px; opacity:.85; margin:6px 0 10px 0; line-height:1.45;}
.ins-bar {display:flex; height:22px; border-radius:8px; overflow:hidden; font-size:11px; font-weight:700; color:#fff;}
.ins-bar i {display:flex; align-items:center; justify-content:center; font-style:normal; white-space:nowrap;}
.ins-track {height:10px; border-radius:6px; background:rgba(128,128,128,.22); overflow:hidden;}
.ins-track i {display:block; height:100%; border-radius:6px; background:var(--c);}
.ins-dots {display:flex; gap:6px; align-items:center; flex-wrap:wrap;}
.ins-dots i {width:12px; height:12px; border-radius:50%; background:rgba(128,128,128,.35);}
.ins-dots i.me {width:20px; height:20px; background:var(--c); box-shadow:0 0 0 3px color-mix(in srgb, var(--c) 30%, transparent);}
.ins-mini {display:flex; justify-content:space-between; font-size:12px; margin-top:6px; opacity:.8;}
.sec {font-size:12px; letter-spacing:3px; font-weight:700; opacity:.6; margin:6px 0 -4px 0;}
.stTabs [data-baseweb="tab-list"] {gap:6px;}
.stTabs [data-baseweb="tab"] {border-radius:10px 10px 0 0; padding:10px 18px; font-weight:600;}
</style>
"""

WELCOME_CSS = """
<style>
[data-testid="stSidebar"], [data-testid="stHeader"], [data-testid="stToolbar"], footer {display:none !important;}
.block-container {padding:0 !important; max-width:100% !important;}
.welcome-wrapper {position:fixed !important; top:0; left:0; width:100vw; height:100vh; z-index:1;
  display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center;
  padding:40px 25px 150px 25px; overflow:hidden; box-sizing:border-box;
  background: radial-gradient(circle at 50% 30%, rgba(0,255,180,.18), transparent 30%),
              radial-gradient(circle at 15% 85%, rgba(0,180,255,.12), transparent 28%),
              linear-gradient(135deg,#020817 0%,#071525 50%,#020817 100%);}
.traffic-light {position:fixed; left:7vw; top:50%; transform:translateY(-50%); background:#050a12;
  border:4px solid rgba(255,255,255,.18); border-radius:45px; padding:45px 38px; width:190px;
  min-height:430px; box-sizing:border-box; box-shadow:0 0 80px rgba(0,255,180,.25);}
.traffic-light div {width:70px; height:70px; border-radius:50%; margin:18px auto;}
.red-light {background:#ff304f; box-shadow:0 0 22px #ff304f;}
.yellow-light {background:#ffd43b; box-shadow:0 0 22px #ffd43b;}
.green-light {background:#00ff88; box-shadow:0 0 30px #00ff88; animation:greenGlow 1.5s infinite;}
.welcome-small {margin-top:28px; font-size:13px; font-weight:700; letter-spacing:5px; color:#00ffb3; animation:textUp 1.3s ease-out;}
.welcome-main {margin-top:18px; font-size:clamp(45px,7vw,90px); line-height:.95; font-weight:900;
  background:linear-gradient(90deg,#00ffb3,#00d9ff,#fff); -webkit-background-clip:text;
  -webkit-text-fill-color:transparent; animation:titleReveal 1.5s ease-out;}
.welcome-name {margin-top:22px; color:#fff; font-size:clamp(22px,3vw,38px); font-weight:800; animation:textUp 1.8s ease-out;}
.welcome-info {max-width:680px; margin-top:18px; color:#b7c7d9; font-size:17px; line-height:1.7; animation:textUp 2.1s ease-out;}
.welcome-hint {margin-top:28px; color:#6f8ba5; font-size:12px; letter-spacing:3px; font-weight:600; animation:textUp 2.4s ease-out;}
.traffic-light.right {left:auto; right:7vw;}
.welcome-info {max-width:760px; font-size:19px;}
.welcome-steps {display:flex; flex-wrap:wrap; justify-content:center; gap:10px; margin-top:22px; animation:textUp 2.3s ease-out;}
.welcome-steps span {padding:8px 16px; border-radius:999px; font-size:11px; font-weight:700; letter-spacing:2px;
  color:#9fe6f2; background:rgba(0,229,255,.07); border:1px solid rgba(0,229,255,.25);}
.welcome-stats {display:flex; flex-wrap:wrap; justify-content:center; gap:34px; margin-top:26px; animation:textUp 2.6s ease-out;}
.welcome-stats div {text-align:center; min-width:110px;}
.welcome-stats b {display:block; font-size:28px; font-weight:900; color:#fff;}
.welcome-stats small {display:block; margin-top:2px; font-size:10px; letter-spacing:2.5px; color:#00ffb3; font-weight:700;}
@media (max-width:1500px) {.traffic-light {transform:translateY(-50%) scale(.6); transform-origin:left center; left:2vw;}
  .traffic-light.right {transform:translateY(-50%) scale(.6); transform-origin:right center; left:auto; right:2vw;}}
@media (max-width:1000px) {.traffic-light {display:none;} .welcome-stats {gap:20px;}}
.st-key-enter_dashboard {position:fixed !important; bottom:5vh; left:50%; transform:translateX(-50%);
  width:min(420px,82vw); z-index:10;}
.st-key-enter_dashboard button {width:100%; padding:16px 28px; border-radius:999px;
  border:1px solid rgba(0,255,180,.5); background:linear-gradient(90deg,rgba(0,255,179,.12),rgba(0,217,255,.12));
  color:#fff; font-size:15px; font-weight:800; letter-spacing:2px; box-shadow:0 0 25px rgba(0,255,180,.15);
  transition:all .3s ease;}
.st-key-enter_dashboard button:hover {border-color:#00ffb3; box-shadow:0 0 35px rgba(0,255,180,.35); transform:scale(1.03);}
@keyframes textUp {from{opacity:0; transform:translateY(20px);} to{opacity:1; transform:translateY(0);}}
@keyframes titleReveal {from{opacity:0; transform:scale(.95);} to{opacity:1; transform:scale(1);}}
@keyframes greenGlow {0%,100%{box-shadow:0 0 20px #00ff88;} 50%{box-shadow:0 0 40px #00ff88;}}
</style>
"""

WELCOME_HTML = """
<div class="welcome-wrapper">
<div class="traffic-light"><div class="red-light"></div><div class="yellow-light"></div><div class="green-light"></div></div>
<div class="traffic-light right"><div class="red-light"></div><div class="yellow-light"></div><div class="green-light"></div></div>
<div class="welcome-small">MATHEMATICS • STATISTICS • OPTIMIZATION</div>
<div class="welcome-main">TRAFFIC,<br>BUT MAKE IT SMART.</div>
<div class="welcome-name">AHMEDABAD TRAFFIC OPTIMIZATION</div>
<div class="welcome-info">Read today's demand. Forecast the city of 2036.<br>Find the signal timings that keep Ahmedabad moving.</div>
<div class="welcome-steps"><span>01 &nbsp;UNDERSTAND DEMAND</span><span>02 &nbsp;EXPLORE 2026 → 2036</span><span>03 &nbsp;OPTIMIZE SIGNALS</span></div>
<div class="welcome-stats">
<div><b>10</b><small>INTERSECTIONS</small></div>
<div><b>80,640</b><small>TRAFFIC RECORDS</small></div>
<div><b>90</b><small>FUTURE SCENARIOS</small></div>
<div><b>10 yrs</b><small>2026 → 2036</small></div>
</div>
<div class="welcome-hint">PRESS ENTER DASHBOARD TO BEGIN ↓</div>
</div>
"""

# ============================================================
# SMALL HELPERS
# ============================================================
def show(fig, key):
    """Render a Plotly figure (works on old and new Streamlit versions)."""
    try:
        st.plotly_chart(fig, width="stretch", key=key)
    except TypeError:
        st.plotly_chart(fig, use_container_width=True, key=key)


def show_df(data, **kw):
    try:
        st.dataframe(data, width="stretch", hide_index=True, **kw)
    except TypeError:
        st.dataframe(data, use_container_width=True, hide_index=True, **kw)


def style(fig, h=380, title=None):
    fig.update_layout(
        height=h,
        margin=dict(l=10, r=10, t=55 if title else 20, b=10),
        title=dict(text=title, x=0, font=dict(size=16)) if title else None,
        legend=dict(orientation="h", y=-0.18, x=0),
    )
    return fig


def card(label, value, sub="", color=C_NOW):
    return (f'<div class="kpi" style="--c:{color}"><div class="kpi-l">{label}</div>'
            f'<div class="kpi-v">{value}</div><div class="kpi-s">{sub}</div></div>')


def section(text):
    st.markdown(f'<div class="sec">{text}</div>', unsafe_allow_html=True)


def image_if_exists(name, caption):
    p = ASSETS / name
    if p.exists():
        st.image(str(p), caption=caption)


def pct(a, b):
    return (a / b - 1) * 100 if b else 0.0


# ============================================================
# WELCOME SCREEN
# ============================================================
if "show_dashboard" not in st.session_state:
    st.session_state.show_dashboard = False

if not st.session_state.show_dashboard:
    st.markdown(WELCOME_CSS, unsafe_allow_html=True)
    st.markdown(WELCOME_HTML, unsafe_allow_html=True)
    if st.button("ENTER DASHBOARD  →", key="enter_dashboard"):
        st.session_state.show_dashboard = True
        st.rerun()
    st.stop()

st.markdown(BASE_CSS, unsafe_allow_html=True)


# ============================================================
# DATA
# ============================================================
def make_demo_data():
    """Synthetic stand-in so the app still opens if the CSV is missing."""
    rng = np.random.default_rng(7)
    names = ["ISKCON Cross Road", "Helmet Cross Road", "Panjrapole", "Nehru Nagar",
             "Shivranjani", "Vastrapur", "Paldi", "Income Tax", "Thaltej", "Gujarat University"]
    base_mix = np.array([48.4, 27.8, 9.0, 4.3, 4.9, 1.9, 3.7])
    fut = {"Low": 1.25, "Moderate": 1.45, "High": 1.70}
    rows, sid = [], 0
    for n in names:
        ns, ew = rng.uniform(3.0, 7.5), rng.uniform(2.5, 6.5)
        mix = base_mix * rng.uniform(0.9, 1.1, 7)
        mix = mix / mix.sum() * 100
        for vs, f in fut.items():
            for comp in COMP_PRESETS:
                if comp == "Custom Mix":
                    continue
                sid += 1
                d = {"Scenario ID": sid, "Intersection": n, "Vehicle Scenario": vs,
                     "Composition Scenario": comp}
                d.update(dict(zip(MIX_COLS, mix)))
                n36, e36 = ns * f * rng.uniform(0.95, 1.05), ew * f * rng.uniform(0.95, 1.05)
                d.update({
                    "Avg Vehicles": (ns + ew) * 2.4,
                    "Traffic Pressure": (ns + ew) / 16,
                    "Avg Waiting Time (sec)": 40 + (ns + ew) * 2.5,
                    "Avg Queue (vehicles)": (ns + ew) * 1.8,
                    "Avg Lane Occupancy (%)": 60 + (ns + ew) * 2.5,
                    "Avg Speed (km/h)": 14 - (ns + ew) * 0.3,
                    "Population 2026": 7000000, "Population 2036": 7703761,
                    "Population Growth (%)": 10.054,
                    "Vehicle Growth (%)": {"Low": 10.0, "Moderate": 15.0, "High": 20.0}[vs],
                    "NS Demand 2026 (veh/min)": ns, "EW Demand 2026 (veh/min)": ew,
                    "NS Demand 2036 (veh/min)": n36, "EW Demand 2036 (veh/min)": e36,
                    "NS Uncertainty": n36 * 0.68, "EW Uncertainty": e36 * 0.62,
                    "Optimal NS Green (sec)": 110 * math.sqrt(n36 * 1.68 / (e36 * 1.62)) /
                                              (1 + math.sqrt(n36 * 1.68 / (e36 * 1.62))),
                    "Optimal EW Green (sec)": 110 - 110 * math.sqrt(n36 * 1.68 / (e36 * 1.62)) /
                                              (1 + math.sqrt(n36 * 1.68 / (e36 * 1.62))),
                })
                rows.append(d)
    return pd.DataFrame(rows)


@st.cache_data(show_spinner=False)
def load_data():
    for p in (BASE_DIR / CSV_NAME, Path.cwd() / CSV_NAME):
        if p.exists():
            return pd.read_csv(p), False
    return make_demo_data(), True


df, IS_DEMO = load_data()


@st.cache_resource(show_spinner="Loading the 80,640 raw 5-minute traffic records (first run only)…")
def load_raw():
    """Raw 5-minute observations (optional). Returns (DataFrame | None, message)."""
    names = ["*synthetic_traffic*.xlsx", "*synthetic_traffic*.csv"]
    cands = [q for folder in (BASE_DIR, Path.cwd()) for pat in names for q in sorted(folder.glob(pat))]
    if not cands:
        return None, "Raw traffic file not found next to app_new.py."
    try:
        p = cands[0]
        raw = pd.read_excel(p) if p.suffix == ".xlsx" else pd.read_csv(p)
        raw["timestamp"] = pd.to_datetime(raw["timestamp"])
        raw["phase"] = np.where(raw["approach"].isin(["North", "South"]), "NS", "EW")
        raw["hour"] = raw["timestamp"].dt.hour
        return raw, ""
    except Exception as e:  # missing openpyxl, bad columns, ...
        return None, f"Could not read the raw traffic file: {e}"


RAW, RAW_MSG = load_raw()

REQUIRED = ["Intersection", "Vehicle Scenario", "Avg Vehicles", "Traffic Pressure",
            "Avg Waiting Time (sec)", "NS Demand 2026 (veh/min)", "EW Demand 2026 (veh/min)",
            "NS Demand 2036 (veh/min)", "EW Demand 2036 (veh/min)",
            "NS Uncertainty", "EW Uncertainty", "Avg Queue (vehicles)", "Avg Lane Occupancy (%)",
            "Avg Speed (km/h)", "Population 2026", "Population 2036", "Population Growth (%)",
            "Vehicle Growth (%)", "Optimal NS Green (sec)", "Optimal EW Green (sec)"] + MIX_COLS
missing = [c for c in REQUIRED if c not in df.columns]
if missing:
    st.error(f"The dataset is missing these columns: {missing}")
    st.stop()

KEYS = ["Intersection", "Vehicle Scenario"]
num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c]) and c not in MIX_COLS]
agg = (df.groupby(KEYS, as_index=False)[num_cols].mean()
         .merge(df.groupby(KEYS, as_index=False)[MIX_COLS].first(), on=KEYS))
agg_idx = agg.set_index(KEYS)

INTERSECTIONS = sorted(df["Intersection"].unique())
VS_ORDER = [v for v in ["Low", "Moderate", "High"] if v in set(df["Vehicle Scenario"])]
VS_ORDER += [v for v in sorted(df["Vehicle Scenario"].unique()) if v not in VS_ORDER]

# ============================================================
# SIDEBAR — CONTROL PANEL
# ============================================================
with st.sidebar:
    st.markdown("## 🚦 Control Panel")
    default_i = INTERSECTIONS.index("ISKCON Cross Road") if "ISKCON Cross Road" in INTERSECTIONS else 0
    sel_i = st.selectbox("📍 Intersection", INTERSECTIONS, index=default_i)

    mode = st.radio("🗓️ Analysis Mode",
                    ["Current Traffic (2026)", "Future Scenario (2036)", "Pick a Year"],
                    index=1)
    if mode.startswith("Current"):
        year = BASE_YEAR
    elif mode.startswith("Future"):
        year = FUTURE_YEAR
    else:
        year = st.slider("Year", BASE_YEAR, FUTURE_YEAR, 2031)

    sel_vs = st.selectbox("📈 Vehicle Growth Scenario", VS_ORDER,
                          index=min(1, len(VS_ORDER) - 1))
    comp_name = st.selectbox("🚗 Vehicle Composition Scenario", list(COMP_PRESETS))

    mults = {t: 1.0 for t in TYPES}
    if COMP_PRESETS[comp_name] is None:
        st.caption("Scale each vehicle share (then re-normalised to 100%).")
        for t in TYPES:
            mults[t] = st.slider(t, 0.2, 2.5, 1.0, 0.05, key=f"mult_{t}")
    else:
        mults.update(COMP_PRESETS[comp_name])

    with st.expander("⚙️ Optimization assumptions"):
        total_green = st.number_input("Total green budget (sec)", 60, 200, 110, 5)
        g_min = st.number_input("Minimum green per phase (sec)", 10, 60, 30, 5)
        g_max = st.number_input("Maximum green per phase (sec)", 50, 120, 80, 5)
        z_val = st.slider("Uncertainty margin (z-score)", 0.0, 1.96, 1.96, 0.05,
                          help="Effective demand = demand + (z / 1.96) × the dataset's uncertainty margin. "
                               "1.96 = the 95% margin used in your report and master dataset; 0 = plain average demand.")
        cur_ns = st.number_input("Current NS green (sec)", 10.0, 120.0, 55.0, 1.0)
        cur_ew = st.number_input("Current EW green (sec)", 10.0, 120.0, 55.0, 1.0)

    with st.expander("🌡️ Pressure status thresholds"):
        P_LOW = st.number_input("Low → Moderate at", 0.1, 3.0, 0.75, 0.05)
        P_HIGH = st.number_input("Moderate → High at", 0.2, 3.0, 0.90, 0.05)
        st.caption("Display convention (the dataset has no official cut-offs). Pressure ≈ 0.7 today.")

    with st.expander("🧮 PCU weights (composition impact)"):
        pcu = {t: st.number_input(t, 0.1, 6.0, DEFAULT_PCU[t], 0.1, key=f"pcu_{t}") for t in TYPES}

    st.divider()
    if st.button("← Back to welcome screen"):
        st.session_state.show_dashboard = False
        st.rerun()
    if IS_DEMO:
        st.warning("CSV not found — showing **synthetic demo data**.")


def status(p):
    if p < P_LOW:
        return "LOW PRESSURE", "🟢", C_OK
    if p < P_HIGH:
        return "MODERATE PRESSURE", "🟡", C_WARN
    return "HIGH PRESSURE", "🔴", C_BAD


# ============================================================
# MODEL FUNCTIONS
# ============================================================
NO_MULT = {t: 1.0 for t in TYPES}


def run_scenario(row, vs, yr, m, z=0.0):
    """Traffic metrics for one intersection / growth scenario / year / mix."""
    t = (yr - BASE_YEAR) / (FUTURE_YEAR - BASE_YEAR)
    base = np.array([float(row[c]) for c in MIX_COLS])
    base = base / base.sum() * 100
    scn = base * np.array([m[k] for k in TYPES])
    scn = scn / scn.sum() * 100
    w = np.array([pcu[k] for k in TYPES])
    pcu_base, pcu_scn = float((base * w).sum() / 100), float((scn * w).sum() / 100)
    comp = pcu_scn / pcu_base

    def interp(a, b):
        a, b = max(float(a), 1e-9), max(float(b), 1e-9)
        return a * (b / a) ** t

    ns0 = interp(row["NS Demand 2026 (veh/min)"], row["NS Demand 2036 (veh/min)"])
    ew0 = interp(row["EW Demand 2026 (veh/min)"], row["EW Demand 2036 (veh/min)"])
    ns, ew = ns0 * comp, ew0 * comp
    # growth in total demand vs 2026 — comes straight from the dataset's own 2036 columns
    scale = (ns0 + ew0) / max(float(row["NS Demand 2026 (veh/min)"] + row["EW Demand 2026 (veh/min)"]), 1e-9)
    load = scale * comp
    # uncertainty margin (dataset gives it for 2036; kept proportional to demand in other years)
    u_ns = float(row["NS Uncertainty"]) / max(float(row["NS Demand 2036 (veh/min)"]), 1e-9)
    u_ew = float(row["EW Uncertainty"]) / max(float(row["EW Demand 2036 (veh/min)"]), 1e-9)
    return dict(
        ns=ns, ew=ew, total=ns + ew,
        ns_eff=ns * (1 + z / 1.96 * u_ns), ew_eff=ew * (1 + z / 1.96 * u_ew),
        vehicles=float(row["Avg Vehicles"]) * scale,
        pressure=float(row["Traffic Pressure"]) * load,
        waiting=float(row["Avg Waiting Time (sec)"]) * load,
        queue=float(row["Avg Queue (vehicles)"]) * load,
        occupancy=min(100.0, float(row["Avg Lane Occupancy (%)"]) * load),
        speed=float(row["Avg Speed (km/h)"]) / load,
        comp=comp, scale=scale, base_mix=base, mix=scn,
        pcu_base=pcu_base, pcu_scn=pcu_scn,
    )


def objective(ns, ew, gn, ge):
    return ns / gn + ew / ge


def optimise(ns, ew, total=None, lo=None, hi=None, cur=(None, None)):
    total = total if total is not None else total_green
    lo = lo if lo is not None else g_min
    hi = hi if hi is not None else g_max
    cn = cur[0] if cur[0] is not None else cur_ns
    ce = cur[1] if cur[1] is not None else cur_ew
    ns, ew = max(ns, 1e-9), max(ew, 1e-9)
    r = math.sqrt(ns / ew)
    g = total * r / (1 + r)                       # g_NS / g_EW = sqrt(D_NS / D_EW)
    lo_b, hi_b = max(lo, total - hi), min(hi, total - lo)
    g = min(max(g, lo_b), hi_b)
    o_now, o_opt = objective(ns, ew, cn, ce), objective(ns, ew, g, total - g)
    return dict(g_ns=g, g_ew=total - g, obj_now=o_now, obj_opt=o_opt,
                improve=(o_now - o_opt) / o_now * 100, lo=lo_b, hi=hi_b)


def network_table(vs, yr, m, z):
    out = []
    for i in INTERSECTIONS:
        r = agg_idx.loc[(i, vs)]
        a, b = run_scenario(r, vs, BASE_YEAR, NO_MULT), run_scenario(r, vs, yr, m, z)
        o = optimise(b["ns_eff"], b["ew_eff"])
        out.append({
            "Intersection": i,
            "Demand 2026": a["total"], "Demand (selected)": b["total"],
            "Growth %": pct(b["total"], a["total"]),
            "Pressure 2026": a["pressure"], "Pressure (selected)": b["pressure"],
            "Waiting (sec)": b["waiting"],
            "NS Demand": b["ns"], "EW Demand": b["ew"],
            "NS Green": o["g_ns"], "EW Green": o["g_ew"],
            "Shift to NS (sec)": o["g_ns"] - cur_ns, "Improvement %": o["improve"],
        })
    return pd.DataFrame(out)


# ============================================================
# ROLLING FORECAST ENGINE  (same method as the project report)
#   Tuesday  = Monday's mean, band = ±1.96 × std of Monday's observations
#   Wed..Sun = mean of the daily means so far, band = ±1.96 × std of those daily means
#   Effective demand D* = forecast + 1.96σ-band;  g_NS / g_EW = sqrt(D*_NS / D*_EW)
# ============================================================
@st.cache_data(show_spinner=False)
def forecast_for(inter):
    if RAW is None:
        return None
    d = RAW[RAW["intersection_name"] == inter]
    if d.empty:
        return None
    col = "arrival_rate_veh_min"
    dp = d.groupby(["day_of_week", "time_band"])[col].mean().unstack().reindex(ALL_DAYS)[PERIODS]
    mon_std = d[d["day_of_week"] == "Monday"].groupby("time_band")[col].std().reindex(PERIODS)
    pred, lo, hi = [], [], []
    for k in range(1, 7):
        h = dp.iloc[:k]
        m = h.mean()
        sp = 1.96 * (mon_std if k == 1 else h.std(ddof=1))
        pred.append(m.values)
        lo.append(np.clip(m - sp, 0, None).values)
        hi.append((m + sp).values)
    # phase level (evening peak): one observation per timestamp and phase
    ev = d[d["time_band"] == "Evening peak"]
    po = ev.groupby(["day_of_week", "timestamp", "phase"])[col].mean().unstack().reset_index()
    dm = po.groupby("day_of_week")[["NS", "EW"]].mean().reindex(ALL_DAYS)
    sd0 = po[po["day_of_week"] == "Monday"][["NS", "EW"]].std()
    eff = []
    for k in range(1, 7):
        h = dm.iloc[:k]
        e = h.mean() + 1.96 * (sd0 if k == 1 else h.std(ddof=1))
        eff.append((DAYS[k - 1], float(e["NS"]), float(e["EW"])))
    diff = po["NS"] - po["EW"]
    n = len(diff)
    t = float(diff.mean() / (diff.std(ddof=1) / math.sqrt(n)))
    mon = d[d["day_of_week"] == "Monday"].groupby("time_band")[col].agg(["mean", "std", "min", "max"]).reindex(PERIODS)
    mon.insert(0, "Time Period", PERIODS)
    return dict(
        pred=np.array(pred), lo=np.array(lo), hi=np.array(hi), act=dp.iloc[1:].values,
        eff=pd.DataFrame(eff, columns=["Day", "NS", "EW"]),
        ns_mean=float(po["NS"].mean()), ew_mean=float(po["EW"].mean()),
        ns_std=float(po["NS"].std()), ew_std=float(po["EW"].std()),
        t=t, p=math.erfc(abs(t) / math.sqrt(2)), n=n,
        period_avg=d.groupby("time_band")[col].mean().reindex(PERIODS).values,
        monday=mon.reset_index(drop=True),
    )


_lo = np.full(PRED.shape, np.nan)
_hi = np.full(PRED.shape, np.nan)
_lo[:, 2], _hi[:, 2] = EVE_LO, EVE_HI
FALLBACK_FC = dict(
    pred=PRED, act=ACT, lo=_lo, hi=_hi,
    eff=pd.DataFrame({"Day": DAYS, "NS": WEEK["NS Demand"], "EW": WEEK["EW Demand"]}),
    ns_mean=6.905, ew_mean=6.032, ns_std=2.381, ew_std=1.838, t=13.61, p=0.0, n=420,
    period_avg=np.array(PERIOD_AVG), monday=None,
)


def week_table(fc):
    rows = []
    for day, ns, ew in fc["eff"].itertuples(index=False):
        o = optimise(ns, ew)
        r_ = {"Day": day, "NS Demand": ns, "EW Demand": ew, "NS Green": o["g_ns"], "EW Green": o["g_ew"]}
        for lab, m_ in [("NS -20%", .8), ("NS -10%", .9), ("NS +10%", 1.1), ("NS +20%", 1.2)]:
            r_[lab] = optimise(ns * m_, ew)["g_ns"]
        rows.append(r_)
    return pd.DataFrame(rows)


# ============================================================
# COMPUTE SELECTED SCENARIO
# ============================================================
row = agg_idx.loc[(sel_i, sel_vs)]
S_now = run_scenario(row, sel_vs, BASE_YEAR, NO_MULT)
S = run_scenario(row, sel_vs, year, mults, z_val)
OPT = optimise(S["ns_eff"], S["ew_eff"])
NET = network_table(sel_vs, year, mults, z_val)
st_label, st_symbol, st_color = status(S["pressure"])
year_txt = "2026 · Current" if year == BASE_YEAR else f"{year} · Future"

# ============================================================
# HERO
# ============================================================
st.markdown(f"""
<div class="hero">
<div class="eyebrow">AHMEDABAD • TRAFFIC ANALYSIS • MATHEMATICAL OPTIMIZATION</div>
<h1>🚦 AHMEDABAD <span>TRAFFIC OPTIMIZATION</span></h1>
<p>A decision-support dashboard: explore today's demand, project it to 2036, and see how
mathematically optimised signal timings respond to growth, vehicle mix and uncertainty.</p>
<span class="chip">📍 {sel_i}</span><span class="chip">🗓️ {year_txt}</span>
<span class="chip">📈 {sel_vs} growth</span><span class="chip">🚗 {comp_name}</span>
<span class="chip">{st_symbol} {st_label}</span>
</div>
""", unsafe_allow_html=True)

# ============================================================
# KPI ROW
# ============================================================
k = st.columns(6)
kpis = [
    ("Traffic Pressure", f"{S['pressure']:.2f}", f"{pct(S['pressure'], S_now['pressure']):+.1f}% vs 2026", st_color),
    ("Average Vehicles", f"{S['vehicles']:.1f}", f"{pct(S['vehicles'], S_now['vehicles']):+.1f}% vs 2026", C_NOW),
    ("Avg Waiting Time", f"{S['waiting']:.1f} s", f"{pct(S['waiting'], S_now['waiting']):+.1f}% vs 2026", C_WARN),
    ("Total Demand", f"{S['total']:.2f}", f"veh/min (PCU-adj.) · {pct(S['total'], S_now['total']):+.1f}% vs 2026", C_FUT),
    ("Optimized Green", f"{OPT['g_ns']:.1f} / {OPT['g_ew']:.1f}", f"NS / EW sec  (now {cur_ns:.0f}/{cur_ew:.0f})", C_NS),
    ("Objective Improvement", f"{OPT['improve']:.2f}%", "reduction in the optimization objective", C_OK),
]
for col, (a, b, c, d) in zip(k, kpis):
    col.markdown(card(a, b, c, d), unsafe_allow_html=True)
st.write("")

tabs = st.tabs(["🏠 Command Center", "🔮 Now vs Future", "🚗 Vehicle Mix",
                "🚦 Signal Optimizer", "📈 Forecast & Validation",
                "🛰️ Raw Traffic Patterns", "🧪 Methodology", "🗂️ Data Explorer"])


# ============================================================
# SVG INTERSECTION DIAGRAM
# ============================================================
def intersection_svg(ns, ew, g_ns, g_ew):
    mx = max(ns, ew, 1e-9)
    wn, we = 3 + 11 * ns / mx, 3 + 11 * ew / mx
    ns_green = g_ns >= g_ew
    return (
        '<svg viewBox="0 0 420 380" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-height:380px">'
        '<rect width="420" height="380" rx="18" fill="#0b1a2c"/>'
        '<rect x="175" y="0" width="70" height="380" fill="#26354a"/>'
        '<rect x="0" y="155" width="420" height="70" fill="#26354a"/>'
        '<rect x="175" y="155" width="70" height="70" fill="#2d3f57"/>'
        '<line x1="210" y1="0" x2="210" y2="150" stroke="#e6edf7" stroke-width="2" stroke-dasharray="10 8" opacity=".5"/>'
        '<line x1="210" y1="230" x2="210" y2="380" stroke="#e6edf7" stroke-width="2" stroke-dasharray="10 8" opacity=".5"/>'
        '<line x1="0" y1="190" x2="170" y2="190" stroke="#e6edf7" stroke-width="2" stroke-dasharray="10 8" opacity=".5"/>'
        '<line x1="250" y1="190" x2="420" y2="190" stroke="#e6edf7" stroke-width="2" stroke-dasharray="10 8" opacity=".5"/>'
        f'<line x1="192" y1="20" x2="192" y2="135" stroke="{C_NS}" stroke-width="{wn:.1f}" stroke-linecap="round" opacity=".9"/>'
        f'<polygon points="192,150 {192 - wn:.1f},130 {192 + wn:.1f},130" fill="{C_NS}"/>'
        f'<line x1="228" y1="360" x2="228" y2="245" stroke="{C_NS}" stroke-width="{wn:.1f}" stroke-linecap="round" opacity=".9"/>'
        f'<polygon points="228,230 {228 - wn:.1f},250 {228 + wn:.1f},250" fill="{C_NS}"/>'
        f'<line x1="20" y1="172" x2="145" y2="172" stroke="{C_EW}" stroke-width="{we:.1f}" stroke-linecap="round" opacity=".9"/>'
        f'<polygon points="165,172 145,{172 - we:.1f} 145,{172 + we:.1f}" fill="{C_EW}"/>'
        f'<line x1="400" y1="208" x2="275" y2="208" stroke="{C_EW}" stroke-width="{we:.1f}" stroke-linecap="round" opacity=".9"/>'
        f'<polygon points="255,208 275,{208 - we:.1f} 275,{208 + we:.1f}" fill="{C_EW}"/>'
        f'<circle cx="160" cy="145" r="9" fill="{C_OK if ns_green else C_BAD}"/>'
        f'<circle cx="260" cy="235" r="9" fill="{C_OK if ns_green else C_BAD}"/>'
        f'<circle cx="160" cy="235" r="9" fill="{C_BAD if ns_green else C_OK}"/>'
        f'<circle cx="260" cy="145" r="9" fill="{C_BAD if ns_green else C_OK}"/>'
        f'<text x="262" y="30" fill="{C_NS}" font-size="14" font-weight="700">NS  {ns:.1f} veh/min</text>'
        f'<text x="262" y="48" fill="#b7c7d9" font-size="12">green {g_ns:.1f} s</text>'
        f'<text x="12" y="140" fill="{C_EW}" font-size="14" font-weight="700">EW  {ew:.1f} veh/min</text>'
        f'<text x="12" y="124" fill="#b7c7d9" font-size="12">green {g_ew:.1f} s</text>'
        '<text x="12" y="368" fill="#6f8ba5" font-size="11">arrow thickness ∝ phase demand</text>'
        '</svg>'
    )


# ============================================================
# TAB 0 — COMMAND CENTER
# ============================================================
with tabs[0]:
    c1, c2, c3 = st.columns([1.1, 1.2, 1.2], gap="large")

    with c1:
        section("TRAFFIC FLOW PULSE")
        gmax_v = max(P_HIGH * 1.5, S["pressure"] * 1.15)
        g = go.Figure(go.Indicator(
            mode="gauge+number+delta", value=S["pressure"],
            delta=dict(reference=S_now["pressure"], relative=True, valueformat=".1%",
                       increasing=dict(color=C_BAD), decreasing=dict(color=C_OK)),
            number=dict(valueformat=".2f"),
            gauge=dict(axis=dict(range=[0, gmax_v]), bar=dict(color=st_color),
                       steps=[dict(range=[0, P_LOW], color="rgba(0,196,140,.25)"),
                              dict(range=[P_LOW, P_HIGH], color="rgba(255,176,32,.25)"),
                              dict(range=[P_HIGH, gmax_v], color="rgba(255,77,94,.25)")]),
            title=dict(text=f"{st_symbol} {st_label}")))
        show(style(g, 300), "gauge")
        st.caption(f"Status bands (editable in the sidebar): < {P_LOW:.2f} low · < {P_HIGH:.2f} moderate · above = high. "
                   "The small delta compares with 2026.")

    with c2:
        section("LIVE INTERSECTION VIEW")
        st.markdown(intersection_svg(S["ns"], S["ew"], OPT["g_ns"], OPT["g_ew"]), unsafe_allow_html=True)

    # ---------- facts used by the verdict + insight cards ----------
    ns_lead = S["ns"] >= S["ew"]
    dom, dom_short = ("North–South", "NS") if ns_lead else ("East–West", "EW")
    gap = abs(pct(S["ns"], S["ew"]))
    shift = OPT["g_ns"] - cur_ns
    worst = NET.sort_values("Pressure (selected)", ascending=False).iloc[0]
    grow = NET.sort_values("Growth %", ascending=False).iloc[0]
    rank = int((NET["Pressure (selected)"] > S["pressure"]).sum()) + 1
    d_dem, d_wait = pct(S["total"], S_now["total"]), pct(S["waiting"], S_now["waiting"])
    arrow = lambda v: "▲" if v > 0.05 else ("▼" if v < -0.05 else "■")
    act_txt = {"HIGH PRESSURE": "🚨 Above the high-pressure line — plan signal or capacity measures.",
               "MODERATE PRESSURE": "👀 Between the thresholds — keep monitoring; re-timing is worthwhile.",
               "LOW PRESSURE": "✅ Comfortable today — standard timing is adequate."}[st_label]

    with c3:
        section("SCENARIO VERDICT")
        st.markdown(
            f'<div class="verdict" style="--c:{st_color}">'
            f'<span class="v-badge">{st_symbol} {st_label}</span>'
            f'<div class="v-head">In {year}, <b>{sel_i}</b> sees demand <b>{d_dem:+.1f}%</b> '
            f'and waiting time <b>{d_wait:+.1f}%</b> versus 2026.</div>'
            f'<div class="v-row">'
            f'<div class="v-pill"><small>PRESSURE</small><span>{S["pressure"]:.2f}</span></div>'
            f'<div class="v-pill"><small>NS GREEN</small><span>{OPT["g_ns"]:.1f}s</span></div>'
            f'<div class="v-pill"><small>EW GREEN</small><span>{OPT["g_ew"]:.1f}s</span></div></div>'
            f'<div class="v-act">{act_txt}<br>Move <b>{abs(shift):.1f} s</b> of green to '
            f'<b>{"NS" if shift >= 0 else "EW"}</b> for a <b>{OPT["improve"]:.2f}%</b> lower objective.</div>'
            f'</div>', unsafe_allow_html=True)

    # ---------- insight cards ----------
    section("KEY INSIGHTS")
    top_dots = "".join(
        f'<i class="me"></i>' if n_ == sel_i else "<i></i>"
        for n_ in NET.sort_values("Pressure (selected)", ascending=False)["Intersection"])
    tot_g = OPT["g_ns"] + OPT["g_ew"]
    max_growth = max(float(NET["Growth %"].max()), 1e-9)
    top3 = NET.sort_values("Pressure (selected)", ascending=False).head(3)
    mix_bar = "".join(f'<i style="width:{v:.1f}%;background:{c_}"></i>' for v, c_ in zip(S["mix"], TYPE_COLORS))
    cards_html = [
        # 1 — rank
        f'<div class="ins" style="--c:{C_FUT}"><div class="ins-top"><div class="ins-ic">📍</div>'
        f'<div class="ins-tag">PRESSURE RANK</div></div>'
        f'<div class="ins-big">#{rank}<small>of {len(NET)} intersections</small></div>'
        f'<div class="ins-txt">Where {sel_i} sits for traffic pressure in {year} ({sel_vs} growth). #1 is the most congested.</div>'
        f'<div class="ins-dots">{top_dots}</div></div>',
        # 2 — dominant phase
        f'<div class="ins" style="--c:{C_NS if ns_lead else C_EW}"><div class="ins-top"><div class="ins-ic">🚦</div>'
        f'<div class="ins-tag">DOMINANT PHASE</div></div>'
        f'<div class="ins-big">{dom_short}<small>+{gap:.1f}% demand</small></div>'
        f'<div class="ins-txt">{dom} carries more traffic, so it earns the larger share of the {tot_g:.0f} s green budget.</div>'
        f'<div class="ins-bar"><i style="width:{OPT["g_ns"] / tot_g * 100:.1f}%;background:{C_NS}">NS {OPT["g_ns"]:.1f}s</i>'
        f'<i style="width:{OPT["g_ew"] / tot_g * 100:.1f}%;background:{C_EW}">EW {OPT["g_ew"]:.1f}s</i></div></div>',
        # 3 — growth
        f'<div class="ins" style="--c:{C_BAD if d_dem > 0 else C_OK}"><div class="ins-top"><div class="ins-ic">📈</div>'
        f'<div class="ins-tag">DEMAND GROWTH</div></div>'
        f'<div class="ins-big">{arrow(d_dem)} {d_dem:+.1f}%<small>vs 2026</small></div>'
        f'<div class="ins-txt">Total demand moves from {S_now["total"]:.1f} to {S["total"]:.1f} veh/min. '
        f'Network peak growth is {grow["Growth %"]:+.1f}% ({grow["Intersection"]}).</div>'
        f'<div class="ins-track"><i style="width:{min(100, max(0, d_dem) / max_growth * 100):.1f}%"></i></div>'
        f'<div class="ins-mini"><span>this intersection</span><span>network max</span></div></div>',
        # 4 — waiting
        f'<div class="ins" style="--c:{C_WARN}"><div class="ins-top"><div class="ins-ic">⏱️</div>'
        f'<div class="ins-tag">WAITING TIME</div></div>'
        f'<div class="ins-big">{S["waiting"]:.0f} s<small>{arrow(d_wait)} {d_wait:+.1f}%</small></div>'
        f'<div class="ins-txt">Average wait per vehicle rises from {S_now["waiting"]:.0f} s to {S["waiting"]:.0f} s; '
        f'queues reach about {S["queue"]:.0f} vehicles.</div>'
        f'<div class="ins-track"><i style="width:{min(100, S_now["waiting"] / max(S["waiting"], 1e-9) * 100):.1f}%;opacity:.45"></i></div>'
        f'<div class="ins-mini"><span>2026: {S_now["waiting"]:.0f}s</span><span>{year}: {S["waiting"]:.0f}s</span></div></div>',
        # 5 — hot-spot
        f'<div class="ins" style="--c:{C_BAD}"><div class="ins-top"><div class="ins-ic">🔥</div>'
        f'<div class="ins-tag">NETWORK HOT-SPOT</div></div>'
        f'<div class="ins-big" style="font-size:22px">{worst["Intersection"]}<small>{worst["Pressure (selected)"]:.2f}</small></div>'
        f'<div class="ins-txt">Highest pressure in the network for this scenario. Top three:</div>'
        + "".join(
            f'<div class="ins-mini" style="margin:3px 0"><span>{r_["Intersection"]}</span><span>{r_["Pressure (selected)"]:.2f}</span></div>'
            f'<div class="ins-track" style="height:6px"><i style="width:{r_["Pressure (selected)"] / max(worst["Pressure (selected)"], 1e-9) * 100:.1f}%"></i></div>'
            for _, r_ in top3.iterrows()) + '</div>',
        # 6 — mix
        f'<div class="ins" style="--c:{C_NOW}"><div class="ins-top"><div class="ins-ic">🚗</div>'
        f'<div class="ins-tag">VEHICLE MIX EFFECT</div></div>' +
        (f'<div class="ins-big">{pct(S["comp"], 1):+.1f}%<small>road load</small></div>' if abs(pct(S["comp"], 1)) >= 0.05
         else '<div class="ins-big">Baseline<small>mix unchanged</small></div>') + (
        f'<div class="ins-txt">{comp_name}: average {S["pcu_base"]:.2f} → {S["pcu_scn"]:.2f} PCU per vehicle. '
        f'Dominant type: {TYPES[int(np.argmax(S["mix"]))]}.</div>'
        f'<div class="ins-bar">{mix_bar}</div></div>'),
    ]
    st.markdown('<div class="ins-grid">' + "".join(cards_html) + '</div>', unsafe_allow_html=True)

    section("NETWORK VIEW — ALL INTERSECTIONS")
    n1, n2 = st.columns(2, gap="large")
    with n1:
        d = NET.sort_values("Pressure (selected)", ascending=False)
        f = go.Figure()
        f.add_bar(x=d["Intersection"], y=d["Pressure 2026"], name="2026", marker_color=C_NOW)
        f.add_bar(x=d["Intersection"], y=d["Pressure (selected)"], name=str(year), marker_color=C_FUT)
        f.add_hline(y=P_HIGH, line_dash="dot", line_color=C_BAD, annotation_text="high-pressure line")
        f.update_layout(barmode="group", yaxis_title="Traffic pressure")
        show(style(f, 380, "Traffic pressure: 2026 vs selected year"), "net_pressure")
    with n2:
        d = NET.sort_values("NS Demand", ascending=False)
        f = go.Figure()
        f.add_bar(x=d["Intersection"], y=d["NS Demand"], name="NS demand", marker_color=C_NS)
        f.add_bar(x=d["Intersection"], y=d["EW Demand"], name="EW demand", marker_color=C_EW)
        f.update_layout(barmode="stack", yaxis_title="veh/min")
        show(style(f, 380, f"Phase demand by intersection ({year})"), "net_phase")


# ============================================================
# TAB 1 — NOW vs FUTURE
# ============================================================
with tabs[1]:
    st.markdown(f"### 2026 vs {year} — {sel_i}")
    a, b, c, d = st.columns(4)
    a.markdown(card("NS demand", f"{S['ns']:.2f}", f"2026: {S_now['ns']:.2f} ({pct(S['ns'], S_now['ns']):+.1f}%)", C_NS), unsafe_allow_html=True)
    b.markdown(card("EW demand", f"{S['ew']:.2f}", f"2026: {S_now['ew']:.2f} ({pct(S['ew'], S_now['ew']):+.1f}%)", C_EW), unsafe_allow_html=True)
    c.markdown(card("Pressure", f"{S['pressure']:.2f}", f"2026: {S_now['pressure']:.2f}", st_color), unsafe_allow_html=True)
    d.markdown(card("Waiting time", f"{S['waiting']:.1f} s", f"2026: {S_now['waiting']:.1f} s", C_WARN), unsafe_allow_html=True)
    st.write("")

    l, r = st.columns(2, gap="large")
    with l:
        f = go.Figure()
        f.add_bar(x=["NS phase", "EW phase"], y=[S_now["ns"], S_now["ew"]], name="2026", marker_color=C_NOW,
                  text=[f"{S_now['ns']:.2f}", f"{S_now['ew']:.2f}"], textposition="outside")
        f.add_bar(x=["NS phase", "EW phase"], y=[S["ns"], S["ew"]], name=str(year), marker_color=C_FUT,
                  text=[f"{S['ns']:.2f}", f"{S['ew']:.2f}"], textposition="outside")
        f.update_layout(barmode="group", yaxis_title="veh/min")
        show(style(f, 400, "Phase demand: now vs future"), "nf_phase")
    with r:
        yrs = list(range(BASE_YEAR, FUTURE_YEAR + 1))
        f = go.Figure()
        paths = {}
        for v in VS_ORDER:
            rv = agg_idx.loc[(sel_i, v)]
            paths[v] = [run_scenario(rv, v, y, mults)["total"] for y in yrs]
        if len(VS_ORDER) > 1:
            f.add_scatter(x=yrs, y=paths[VS_ORDER[-1]], line=dict(width=0), showlegend=False, hoverinfo="skip")
            f.add_scatter(x=yrs, y=paths[VS_ORDER[0]], fill="tonexty", line=dict(width=0),
                          fillcolor="rgba(124,77,255,.15)", name="Scenario range", hoverinfo="skip")
        for v, col in zip(VS_ORDER, [C_OK, C_WARN, C_BAD, C_FUT]):
            f.add_scatter(x=yrs, y=paths[v], mode="lines+markers", name=f"{v} growth",
                          line=dict(width=4 if v == sel_vs else 2, color=col))
        f.add_vline(x=year, line_dash="dot", annotation_text=str(year))
        f.update_layout(xaxis_title="Year", yaxis_title="Total demand (veh/min)")
        show(style(f, 400, "Demand trajectory 2026 → 2036 by growth scenario"), "nf_traj")

    l, r = st.columns(2, gap="large")
    with l:
        d = NET.sort_values("Demand (selected)")
        f = go.Figure()
        for _, rr in d.iterrows():
            f.add_scatter(x=[rr["Demand 2026"], rr["Demand (selected)"]], y=[rr["Intersection"]] * 2,
                          mode="lines", line=dict(color="rgba(150,150,150,.6)", width=3), showlegend=False, hoverinfo="skip")
        f.add_scatter(x=d["Demand 2026"], y=d["Intersection"], mode="markers", name="2026",
                      marker=dict(size=12, color=C_NOW))
        f.add_scatter(x=d["Demand (selected)"], y=d["Intersection"], mode="markers", name=str(year),
                      marker=dict(size=12, color=C_FUT))
        f.update_layout(xaxis_title="Total demand (veh/min)")
        show(style(f, 420, "Demand shift by intersection (dumbbell)"), "nf_dumbbell")
    with r:
        mat = []
        for i in INTERSECTIONS:
            line = []
            for v in VS_ORDER:
                rv = agg_idx.loc[(i, v)]
                t26 = rv["NS Demand 2026 (veh/min)"] + rv["EW Demand 2026 (veh/min)"]
                t36 = rv["NS Demand 2036 (veh/min)"] + rv["EW Demand 2036 (veh/min)"]
                line.append(pct(t36, t26))
            mat.append(line)
        f = go.Figure(go.Heatmap(z=mat, x=VS_ORDER, y=INTERSECTIONS, colorscale="YlOrRd",
                                 texttemplate="%{z:.0f}%", colorbar=dict(title="% growth")))
        show(style(f, 420, "Demand growth 2026 → 2036 (intersection × scenario)"), "nf_heat")

    # pressure timeline for every intersection
    rows_ = []
    for i in INTERSECTIONS:
        ri = agg_idx.loc[(i, sel_vs)]
        for y in range(BASE_YEAR, FUTURE_YEAR + 1):
            rows_.append({"Year": y, "Intersection": i, "Pressure": run_scenario(ri, sel_vs, y, mults)["pressure"]})
    tl = pd.DataFrame(rows_)
    f = px.line(tl, x="Year", y="Pressure", color="Intersection", markers=True)
    f.add_hline(y=P_HIGH, line_dash="dot", line_color=C_BAD, annotation_text="high-pressure threshold")
    f.update_traces(line=dict(width=2))
    show(style(f, 400, f"Traffic-pressure timeline — {sel_vs} growth, {comp_name}"), "nf_timeline")


    st.markdown("#### 👥 What drives the growth — and what it does on the road")
    pop26, pop36 = float(row["Population 2026"]), float(row["Population 2036"])
    q1, q2, q3, q4 = st.columns(4)
    q1.markdown(card("Population", f"{pop36 / 1e6:.2f} M", f"2036 · from {pop26 / 1e6:.2f} M in 2026 ({row['Population Growth (%)']:+.1f}%)", C_NOW), unsafe_allow_html=True)
    q2.markdown(card("Avg queue", f"{S['queue']:.1f}", f"vehicles · 2026: {S_now['queue']:.1f}", C_WARN), unsafe_allow_html=True)
    q3.markdown(card("Lane occupancy", f"{S['occupancy']:.1f}%", f"2026: {S_now['occupancy']:.1f}%", C_BAD), unsafe_allow_html=True)
    q4.markdown(card("Avg speed", f"{S['speed']:.1f} km/h", f"2026: {S_now['speed']:.1f} km/h", C_FUT), unsafe_allow_html=True)
    st.write("")
    l, r = st.columns(2, gap="large")
    with l:
        gd = []
        for v in VS_ORDER:
            rv = agg_idx.loc[(sel_i, v)]
            t26 = rv["NS Demand 2026 (veh/min)"] + rv["EW Demand 2026 (veh/min)"]
            t36 = rv["NS Demand 2036 (veh/min)"] + rv["EW Demand 2036 (veh/min)"]
            gd.append((v, float(rv["Population Growth (%)"]), float(rv["Vehicle Growth (%)"]), pct(t36, t26)))
        f = go.Figure()
        f.add_bar(x=[g[0] for g in gd], y=[g[1] for g in gd], name="Population growth", marker_color=C_NOW)
        f.add_bar(x=[g[0] for g in gd], y=[g[2] for g in gd], name="Vehicle growth", marker_color=C_FUT)
        f.add_bar(x=[g[0] for g in gd], y=[g[3] for g in gd], name="Resulting demand growth", marker_color=C_BAD,
                  text=[f"{g[3]:.1f}%" for g in gd], textposition="outside")
        f.update_layout(barmode="group", yaxis_title="Growth 2026 → 2036 (%)")
        show(style(f, 380, "Growth drivers by scenario (demand ≈ population × vehicles)"), "nf_drivers")
    with r:
        keys_ = [("Demand", "total"), ("Vehicles", "vehicles"), ("Waiting time", "waiting"), ("Queue", "queue"),
                 ("Occupancy", "occupancy"), ("Pressure", "pressure"), ("Speed", "speed")]
        idx = [S[k_] / S_now[k_] * 100 for _, k_ in keys_]
        f = go.Figure(go.Bar(x=[n_ for n_, _ in keys_], y=idx,
                             marker_color=[C_OK if v < 100 else C_BAD for v in idx],
                             text=[f"{v:.0f}" for v in idx], textposition="outside"))
        f.add_hline(y=100, line_dash="dot", annotation_text="2026 = 100")
        f.update_layout(yaxis_title="Index (2026 = 100)")
        show(style(f, 380, f"Impact index in {year} vs 2026"), "nf_index")


# ============================================================
# TAB 2 — VEHICLE MIX
# ============================================================
with tabs[2]:
    st.markdown(f"### Vehicle composition — {sel_i}")
    a, b, c, d = st.columns(4)
    a.markdown(card("Composition factor", f"{S['comp']:.3f}", "PCU load vs current mix", C_FUT), unsafe_allow_html=True)
    b.markdown(card("Avg PCU / vehicle (now)", f"{S['pcu_base']:.2f}", "current mix", C_NOW), unsafe_allow_html=True)
    c.markdown(card("Avg PCU / vehicle (scenario)", f"{S['pcu_scn']:.2f}", comp_name, C_WARN), unsafe_allow_html=True)
    top = TYPES[int(np.argmax(S["mix"]))]
    d.markdown(card("Dominant vehicle", top, f"{S['mix'].max():.1f}% of traffic", C_OK), unsafe_allow_html=True)
    st.write("")

    l, r = st.columns(2, gap="large")
    with l:
        f = go.Figure(go.Pie(labels=TYPES, values=S["base_mix"], hole=.55, marker=dict(colors=TYPE_COLORS),
                             textinfo="label+percent", sort=False))
        show(style(f, 380, "Current vehicle mix"), "vm_pie_now")
    with r:
        f = go.Figure(go.Pie(labels=TYPES, values=S["mix"], hole=.55, marker=dict(colors=TYPE_COLORS),
                             textinfo="label+percent", sort=False))
        show(style(f, 380, f"Scenario mix — {comp_name}"), "vm_pie_scn")

    l, r = st.columns(2, gap="large")
    with l:
        delta = S["mix"] - S["base_mix"]
        f = go.Figure(go.Bar(x=TYPES, y=delta, marker_color=[C_OK if v >= 0 else C_BAD for v in delta],
                             text=[f"{v:+.2f}" for v in delta], textposition="outside"))
        f.update_layout(yaxis_title="Change in share (percentage points)")
        show(style(f, 380, "Shift in vehicle share"), "vm_delta")
    with r:
        w = np.array([pcu[t] for t in TYPES])
        f = go.Figure()
        f.add_bar(x=TYPES, y=S["base_mix"] * w / 100, name="Current", marker_color=C_NOW)
        f.add_bar(x=TYPES, y=S["mix"] * w / 100, name="Scenario", marker_color=C_FUT)
        f.update_layout(barmode="group", yaxis_title="PCU contribution per vehicle")
        show(style(f, 380, "Who creates the road load? (share × PCU weight)"), "vm_pcu")

    l, r = st.columns(2, gap="large")
    with l:
        long = agg[agg["Vehicle Scenario"] == sel_vs][["Intersection"] + MIX_COLS].melt(
            "Intersection", var_name="Type", value_name="Share")
        long["Type"] = long["Type"].str.replace(" (%)", "", regex=False)
        f = px.bar(long, x="Intersection", y="Share", color="Type", color_discrete_sequence=TYPE_COLORS,
                   category_orders={"Type": TYPES})
        f.update_layout(barmode="stack", yaxis_title="Share (%)")
        show(style(f, 400, "Baseline composition across the network"), "vm_stack")
    with r:
        rows_ = []
        for nm, mm in COMP_PRESETS.items():
            m2 = NO_MULT.copy()
            if mm is None:
                m2 = mults
            else:
                m2.update(mm)
            s2 = run_scenario(row, sel_vs, year, m2)
            rows_.append({"Mix": nm, "Total demand": s2["total"], "Pressure": s2["pressure"]})
        wi = pd.DataFrame(rows_)
        f = go.Figure()
        f.add_bar(x=wi["Mix"], y=wi["Total demand"], marker_color=[C_FUT if m == comp_name else "#8892a6" for m in wi["Mix"]],
                  text=wi["Total demand"].round(2), textposition="outside", name="Total demand")
        f.update_layout(yaxis_title="PCU-adjusted demand (veh/min)", showlegend=False)
        show(style(f, 400, f"What-if: same year ({year}), different mixes"), "vm_whatif")

    f = px.treemap(long, path=[px.Constant("Network"), "Intersection", "Type"], values="Share",
                   color="Type", color_discrete_sequence=TYPE_COLORS)
    show(style(f, 440, "Composition treemap (size = share)"), "vm_tree")
    st.info("Composition changes the **volume of road load** (PCU) on both phases equally, so it changes "
            "pressure, waiting time and objective value — but not the NS/EW split of green time.")


# ============================================================
# TAB 3 — SIGNAL OPTIMIZER
# ============================================================
with tabs[3]:
    st.markdown(f"### Signal timing optimization — {sel_i} ({year})")
    a, b, c, d = st.columns(4)
    a.markdown(card("Optimized NS green", f"{OPT['g_ns']:.2f} s", f"current {cur_ns:.0f} s ({OPT['g_ns'] - cur_ns:+.2f})", C_NS), unsafe_allow_html=True)
    b.markdown(card("Optimized EW green", f"{OPT['g_ew']:.2f} s", f"current {cur_ew:.0f} s ({OPT['g_ew'] - cur_ew:+.2f})", C_EW), unsafe_allow_html=True)
    c.markdown(card("Objective (now → opt.)", f"{OPT['obj_now']:.4f} → {OPT['obj_opt']:.4f}", "Σ demand ÷ green time", C_FUT), unsafe_allow_html=True)
    d.markdown(card("Improvement", f"{OPT['improve']:.2f}%", "vs current timing", C_OK), unsafe_allow_html=True)
    st.caption(f"Cross-check: your master dataset's own optimum for {sel_i} is NS "
               f"{row['Optimal NS Green (sec)']:.2f} s / EW {row['Optimal EW Green (sec)']:.2f} s (2036, 95% margin). "
               "Choose year 2036, current mix and z = 1.96 to reproduce it exactly.")
    st.write("")

    l, r = st.columns(2, gap="large")
    with l:
        gs = np.linspace(OPT["lo"], OPT["hi"], 200)
        ys = S["ns_eff"] / gs + S["ew_eff"] / (total_green - gs)
        f = go.Figure()
        f.add_scatter(x=gs, y=ys, mode="lines", line=dict(color=C_FUT, width=3), name="Objective")
        f.add_scatter(x=[cur_ns], y=[OPT["obj_now"]], mode="markers+text", text=["Current"], textposition="top center",
                      marker=dict(size=14, color=C_WARN), name="Current")
        f.add_scatter(x=[OPT["g_ns"]], y=[OPT["obj_opt"]], mode="markers+text", text=["Optimum"], textposition="bottom center",
                      marker=dict(size=16, color=C_OK, symbol="star"), name="Optimum")
        f.update_layout(xaxis_title="NS green time (sec)  —  EW = budget − NS", yaxis_title="Objective")
        show(style(f, 400, "The optimisation landscape (convex → one clear minimum)"), "so_curve")
    with r:
        f = go.Figure()
        for lab, gn, ge in [("Optimized", OPT["g_ns"], OPT["g_ew"]), ("Current", cur_ns, cur_ew)]:
            f.add_bar(y=[lab], x=[gn], orientation="h", marker_color=C_NS, name="NS green" if lab == "Optimized" else None,
                      showlegend=lab == "Optimized", text=[f"NS {gn:.1f}s"], textposition="inside")
            f.add_bar(y=[lab], x=[ge], orientation="h", marker_color=C_EW, name="EW green" if lab == "Optimized" else None,
                      showlegend=lab == "Optimized", text=[f"EW {ge:.1f}s"], textposition="inside")
        f.update_layout(barmode="stack", xaxis_title="seconds in the signal cycle")
        show(style(f, 400, "Signal cycle: current vs optimized"), "so_cycle")

    st.markdown("#### 🎚️ Sensitivity — what if demand differs from the forecast?")
    s1, s2 = st.columns([1, 2.2], gap="large")
    with s1:
        dn = st.slider("NS demand change (%)", -30, 30, 0, 5)
        de = st.slider("EW demand change (%)", -30, 30, 0, 5)
        o2 = optimise(S["ns_eff"] * (1 + dn / 100), S["ew_eff"] * (1 + de / 100))
        st.markdown(card("Re-optimised NS / EW", f"{o2['g_ns']:.2f} / {o2['g_ew']:.2f} s",
                         f"improvement {o2['improve']:.2f}% vs current", C_NS), unsafe_allow_html=True)
    with s2:
        deltas = list(range(-30, 31, 5))
        f = go.Figure()
        f.add_scatter(x=deltas, y=[optimise(S["ns_eff"] * (1 + x / 100), S["ew_eff"])["g_ns"] for x in deltas],
                      mode="lines+markers", line=dict(color=C_NS, width=3), name="Optimal NS green")
        f.add_scatter(x=[dn], y=[optimise(S["ns_eff"] * (1 + dn / 100), S["ew_eff"])["g_ns"]], mode="markers",
                      marker=dict(size=16, color=C_WARN), name="Your NS setting")
        f.add_hline(y=cur_ns, line_dash="dot", annotation_text="current NS green")
        f.update_layout(xaxis_title="NS demand change (%)", yaxis_title="Optimal NS green (sec)")
        show(style(f, 340, "Optimal NS green vs NS demand change"), "so_sens")

    grid = [-20, -10, 0, 10, 20]
    z = [[optimise(S["ns_eff"] * (1 + x / 100), S["ew_eff"] * (1 + y / 100))["g_ns"] for x in grid] for y in grid]
    f = go.Figure(go.Heatmap(z=z, x=[f"NS {x:+d}%" for x in grid], y=[f"EW {y:+d}%" for y in grid],
                             colorscale="RdBu", reversescale=True, texttemplate="%{z:.1f}",
                             colorbar=dict(title="NS green (s)")))
    show(style(f, 380, "Optimal NS green — joint NS × EW demand shocks"), "so_heat")

    st.markdown("#### 🌆 Optimised timings for the whole network")
    d = NET.sort_values("Shift to NS (sec)")
    f = go.Figure(go.Bar(x=d["Shift to NS (sec)"], y=d["Intersection"], orientation="h",
                         marker_color=[C_NS if v >= 0 else C_EW for v in d["Shift to NS (sec)"]],
                         text=[f"{v:+.2f}s" for v in d["Shift to NS (sec)"]], textposition="outside"))
    f.update_layout(xaxis_title="Green seconds moved to NS (negative = moved to EW)")
    show(style(f, 400, "Where does the model move green time?"), "so_shift")
    show_df(NET[["Intersection", "NS Demand", "EW Demand", "NS Green", "EW Green",
                 "Shift to NS (sec)", "Improvement %"]].round(2))


# ============================================================
# TAB 4 — FORECAST & VALIDATION (computed live from the raw 5-minute data)
# ============================================================
with tabs[4]:
    live = RAW is not None
    FC = forecast_for(sel_i) if live else FALLBACK_FC
    fc_name = sel_i if live else "ISKCON Cross Road"
    st.markdown(f"### Rolling forecast, validation & weekly signal plan — {fc_name}")
    if live:
        st.caption("Computed live from the raw 5-minute records with the method in your report "
                   "(Monday → Tuesday, Monday–Tuesday → Wednesday, …). Change the intersection in the sidebar to repeat it anywhere.")
    else:
        st.warning(f"{RAW_MSG} Showing the saved report results for ISKCON Cross Road instead. "
                   "Place the raw Excel file next to app_new.py to compute this for every intersection.")

    WK = week_table(FC)
    pred, act, lo_, hi_ = FC["pred"], FC["act"], FC["lo"], FC["hi"]
    err = act - pred
    mae = np.abs(err).mean(axis=1)
    mape = (np.abs(err) / act).mean(axis=1) * 100
    accd = 100 - mape
    best = int(np.argmax(accd))

    a, b, c, d, e = st.columns(5)
    a.markdown(card("NS evening demand", f"{FC['ns_mean']:.2f}", f"veh/min · σ = {FC['ns_std']:.2f}", C_NS), unsafe_allow_html=True)
    b.markdown(card("EW evening demand", f"{FC['ew_mean']:.2f}", f"veh/min · σ = {FC['ew_std']:.2f}", C_EW), unsafe_allow_html=True)
    c.markdown(card("Paired t-test (NS vs EW)", f"t = {FC['t']:.2f}",
                    "p < 0.001 → significant" if FC["p"] < 0.001 else f"p = {FC['p']:.3f}", C_FUT), unsafe_allow_html=True)
    d.markdown(card(f"Best day ({DAYS[best][:3]})", f"{accd[best]:.2f}%", f"forecast accuracy · MAE {mae[best]:.2f}", C_OK), unsafe_allow_html=True)
    e.markdown(card("Weekly avg optimized", f"{WK['NS Green'].mean():.2f} / {WK['EW Green'].mean():.2f} s",
                    "NS / EW vs 55 / 55 today", C_WARN), unsafe_allow_html=True)
    st.write("")

    l, r = st.columns(2, gap="large")
    with l:
        pa = FC["period_avg"]
        f = go.Figure(go.Bar(x=PERIODS, y=pa, marker_color=[C_BAD if p_ == "Evening peak" else C_NOW for p_ in PERIODS],
                             text=[f"{v:.2f}" for v in pa], textposition="outside"))
        f.update_layout(yaxis_title="Average arrival rate (veh/min)")
        show(style(f, 380, "Demand by time period"), "fc_period")
    with r:
        per = st.selectbox("Time period for predicted vs actual", ["All periods (average)"] + PERIODS, key="fc_per")
        f = go.Figure()
        if per.startswith("All"):
            p_, a_ = pred.mean(axis=1), act.mean(axis=1)
        else:
            j = PERIODS.index(per)
            p_, a_ = pred[:, j], act[:, j]
            if not np.isnan(hi_[:, j]).any():
                f.add_scatter(x=DAYS, y=hi_[:, j], line=dict(width=0), showlegend=False, hoverinfo="skip")
                f.add_scatter(x=DAYS, y=lo_[:, j], fill="tonexty", line=dict(width=0),
                              fillcolor="rgba(124,77,255,.15)", name="95% band", hoverinfo="skip")
        f.add_scatter(x=DAYS, y=p_, mode="lines+markers", name="Predicted", line=dict(color=C_FUT, width=3))
        f.add_scatter(x=DAYS, y=a_, mode="lines+markers", name="Actual", line=dict(color=C_WARN, width=3))
        f.update_layout(yaxis_title="veh/min")
        show(style(f, 380, f"Predicted vs actual — {per}"), "fc_pva")

    l, r = st.columns([1.3, 1], gap="large")
    with l:
        f = go.Figure(go.Heatmap(z=err, x=PERIODS, y=DAYS, colorscale="RdBu", zmid=0, reversescale=True,
                                 texttemplate="%{z:+.2f}", colorbar=dict(title="Actual − Pred")))
        show(style(f, 380, "Forecast error by day × period"), "fc_err")
    with r:
        show_df(pd.DataFrame({"Day": DAYS, "MAE": mae.round(3), "MAPE %": mape.round(2), "Accuracy %": accd.round(2)}))
        f = go.Figure(go.Bar(x=DAYS, y=accd, marker_color=[C_OK if v > 95 else C_WARN if v > 85 else C_BAD for v in accd],
                             text=[f"{v:.1f}" for v in accd], textposition="outside"))
        f.update_layout(yaxis=dict(range=[max(0, min(accd) - 8), 101], title="Accuracy (%)"))
        show(style(f, 260, "Forecast accuracy (weekends are harder)"), "fc_acc")

    with st.expander("📋 Prediction ranges for a chosen day (like the report's tables)"):
        dsel = st.selectbox("Day", DAYS, key="fc_range_day")
        k = DAYS.index(dsel)
        tbl = pd.DataFrame({"Time Period": PERIODS, "Predicted": pred[k], "Lower (95%)": lo_[k], "Upper (95%)": hi_[k],
                            "Actual": act[k], "Error": act[k] - pred[k]}).round(2)
        show_df(tbl)
        if FC["monday"] is not None:
            st.caption("Monday observed traffic — the training data for Tuesday's forecast:")
            show_df(FC["monday"].round(2).rename(columns={"mean": "Average", "std": "Std. Dev", "min": "Min", "max": "Max"}))

    st.markdown("#### 🚦 Weekly optimised signal plan")
    l, r = st.columns(2, gap="large")
    with l:
        f = go.Figure()
        f.add_scatter(x=DAYS, y=WK["NS Green"], mode="lines+markers", name="Optimized NS", line=dict(color=C_NS, width=3))
        f.add_scatter(x=DAYS, y=WK["EW Green"], mode="lines+markers", name="Optimized EW", line=dict(color=C_EW, width=3))
        f.add_hline(y=cur_ns, line_dash="dot", annotation_text=f"current {cur_ns:.0f} s")
        f.update_layout(yaxis_title="Green time (sec)")
        show(style(f, 380, "Current vs optimized green time"), "fc_green")
    with r:
        f = go.Figure()
        for col_, colr in [("NS -20%", "#1f77b4"), ("NS -10%", "#ff7f0e"), ("NS Green", "#2ca02c"),
                           ("NS +10%", "#d62728"), ("NS +20%", "#9467bd")]:
            f.add_scatter(x=DAYS, y=WK[col_], mode="lines+markers", line=dict(color=colr, width=3 if col_ == "NS Green" else 2),
                          name="Baseline" if col_ == "NS Green" else col_.replace("NS ", "NS demand "))
        f.update_layout(yaxis_title="Optimal NS green (sec)")
        show(style(f, 380, "Sensitivity of optimal NS green (±10%, ±20%)"), "fc_sens")

    st.markdown("#### 🧮 Try the model on any forecast day")
    p1, p2 = st.columns([1, 2], gap="large")
    with p1:
        day = st.selectbox("Day", DAYS, key="calc_day")
        dd = st.slider("NS demand shock (%)", -30, 30, 0, 5, key="calc_shock")
        w_ = WK[WK["Day"] == day].iloc[0]
        oc = optimise(w_["NS Demand"] * (1 + dd / 100), w_["EW Demand"])
        st.markdown(card("Recommended NS / EW", f"{oc['g_ns']:.2f} / {oc['g_ew']:.2f} s",
                         f"effective demand NS {w_['NS Demand'] * (1 + dd / 100):.2f} · EW {w_['EW Demand']:.2f}", C_NS),
                    unsafe_allow_html=True)
    with p2:
        f = go.Figure()
        f.add_bar(x=DAYS, y=WK["NS Demand"], name="NS effective demand", marker_color=C_NS)
        f.add_bar(x=DAYS, y=WK["EW Demand"], name="EW effective demand", marker_color=C_EW)
        f.update_layout(barmode="group", yaxis_title="veh/min (forecast + 95% margin)")
        show(style(f, 330, "Forecast effective demand per phase"), "fc_eff")
    st.caption("Tuesday is predicted from Monday alone, so its uncertainty band is widest — the model adds the largest "
               "safety margin and moves the most green time to the heavier phase.")
    show_df(WK.round(2))


# ============================================================
# TAB 5 — RAW TRAFFIC PATTERNS (80,640 five-minute records)
# ============================================================
with tabs[5]:
    if RAW is None:
        st.info(f"{RAW_MSG}\n\nPut `ahmedabad_synthetic_traffic_7days_5min.xlsx` in the same folder as `app_new.py` "
                "(and make sure `openpyxl` is installed) to unlock this tab.")
    else:
        D = RAW[RAW["intersection_name"] == sel_i]
        AR = "arrival_rate_veh_min"
        hr = D.groupby("hour")[AR].mean()
        hs = D["congestion_level"].isin(["High", "Severe"]).mean() * 100
        st.markdown(f"### What the raw traffic looks like — {sel_i}")
        st.caption("Source: the 5-minute dataset (7 days × 4 approaches). Every record is labelled "
                   "`SYNTHETIC_NOT_OBSERVED`, so treat patterns as a simulation of Ahmedabad traffic.")
        a, b, c, d, e = st.columns(5)
        a.markdown(card("Records", f"{len(D):,}", "5-minute observations", C_NOW), unsafe_allow_html=True)
        b.markdown(card("Avg arrival rate", f"{D[AR].mean():.2f}", "veh/min per approach", C_FUT), unsafe_allow_html=True)
        c.markdown(card("Busiest hour", f"{int(hr.idxmax()):02d}:00", f"{hr.max():.2f} veh/min", C_BAD), unsafe_allow_html=True)
        d.markdown(card("High / Severe congestion", f"{hs:.1f}%", "of 5-minute records", C_WARN), unsafe_allow_html=True)
        e.markdown(card("Avg waiting time", f"{D['avg_wait_sec'].mean():.1f} s", f"avg speed {D['avg_speed_kmph'].mean():.1f} km/h", C_OK), unsafe_allow_html=True)
        st.write("")

        l, r = st.columns(2, gap="large")
        with l:
            pv = D.pivot_table(index="day_of_week", columns="hour", values=AR, aggfunc="mean").reindex(ALL_DAYS)
            f = go.Figure(go.Heatmap(z=pv.values, x=[f"{h:02d}h" for h in pv.columns], y=pv.index,
                                     colorscale="YlOrRd", colorbar=dict(title="veh/min")))
            f.update_yaxes(autorange="reversed")
            show(style(f, 400, "When does it get busy? (day × hour)"), "rp_heat")
        with r:
            wk = D.groupby(["is_weekend", "hour"])[AR].mean().unstack(0)
            f = go.Figure()
            if 0 in wk.columns:
                f.add_scatter(x=wk.index, y=wk[0], mode="lines+markers", name="Weekday", line=dict(color=C_NOW, width=3))
            if 1 in wk.columns:
                f.add_scatter(x=wk.index, y=wk[1], mode="lines+markers", name="Weekend", line=dict(color=C_FUT, width=3))
            f.update_layout(xaxis_title="Hour of day", yaxis_title="veh/min")
            show(style(f, 400, "Weekday vs weekend demand profile"), "rp_week")

        l, r = st.columns(2, gap="large")
        with l:
            ap = D.groupby(["time_band", "approach"])[AR].mean().reset_index()
            f = px.bar(ap, x="time_band", y=AR, color="approach", barmode="group",
                       category_orders={"time_band": PERIODS, "approach": ["North", "South", "East", "West"]},
                       color_discrete_sequence=[C_NS, "#6aa9ff", C_EW, "#ffc08a"])
            f.update_layout(xaxis_title="", yaxis_title="veh/min")
            show(style(f, 380, "Demand by approach and time band"), "rp_approach")
        with r:
            ct = pd.crosstab(D["time_band"], D["congestion_level"], normalize="index").reindex(PERIODS) * 100
            f = go.Figure()
            for lvl in ["Low", "Moderate", "High", "Severe"]:
                if lvl in ct.columns:
                    f.add_bar(x=ct.index, y=ct[lvl], name=lvl, marker_color=CONG_COLORS[lvl])
            f.update_layout(barmode="stack", yaxis_title="% of records")
            show(style(f, 380, "Congestion level by time band"), "rp_cong")

        l, r = st.columns(2, gap="large")
        with l:
            wx = D.groupby(["weather", "event_flag"])["avg_wait_sec"].mean().reset_index()
            wx["Event"] = np.where(wx["event_flag"] == 1, "Event day-part", "No event")
            f = px.bar(wx, x="weather", y="avg_wait_sec", color="Event", barmode="group",
                       color_discrete_sequence=[C_NOW, C_BAD])
            f.update_layout(xaxis_title="", yaxis_title="Avg waiting time (sec)")
            show(style(f, 380, "Does weather or an event add waiting time?"), "rp_weather")
        with r:
            smp = D.sample(min(3000, len(D)), random_state=1)
            f = px.scatter(smp, x="lane_occupancy_pct", y="avg_speed_kmph", color="congestion_level",
                           color_discrete_map=CONG_COLORS, opacity=.6,
                           category_orders={"congestion_level": ["Low", "Moderate", "High", "Severe"]})
            f.update_layout(xaxis_title="Lane occupancy (%)", yaxis_title="Speed (km/h)")
            show(style(f, 380, "Fundamental diagram: occupancy vs speed"), "rp_scatter")

        st.markdown("#### 🌆 Network comparison (all 10 intersections)")
        l, r = st.columns(2, gap="large")
        with l:
            nb = RAW.pivot_table(index="intersection_name", columns="time_band", values=AR, aggfunc="mean")[PERIODS]
            nb = nb.loc[nb.mean(axis=1).sort_values().index]
            f = go.Figure(go.Heatmap(z=nb.values, x=nb.columns, y=nb.index, colorscale="YlOrRd",
                                     texttemplate="%{z:.1f}", colorbar=dict(title="veh/min")))
            show(style(f, 420, "Average demand: intersection × time band"), "rp_net")
        with r:
            sv = (RAW["congestion_level"].isin(["High", "Severe"]).groupby(RAW["intersection_name"]).mean() * 100).sort_values()
            f = go.Figure(go.Bar(x=sv.values, y=sv.index, orientation="h",
                                 marker_color=[C_FUT if n_ == sel_i else "#8892a6" for n_ in sv.index],
                                 text=[f"{v:.1f}%" for v in sv.values], textposition="outside"))
            f.update_layout(xaxis_title="% of 5-minute records in High / Severe congestion")
            show(style(f, 420, "Congestion hot-spots"), "rp_hot")

        l, r = st.columns(2, gap="large")
        with l:
            vc = ["two_wheeler", "car", "auto_rickshaw", "bus", "light_commercial", "heavy_truck", "bicycle"]
            obs = D[vc].sum()
            obs = obs / obs.sum() * 100
            f = go.Figure()
            f.add_bar(x=TYPES, y=obs.values, name="Observed (raw 5-min data)", marker_color=C_NOW)
            f.add_bar(x=TYPES, y=S_now["base_mix"], name="Master dataset (%)", marker_color=C_FUT)
            f.update_layout(barmode="group", yaxis_title="Share (%)")
            show(style(f, 380, "Vehicle mix: raw data vs master dataset"), "rp_mix")
        with r:
            vio = RAW.groupby("intersection_name").agg(sj=("signal_jump_count", "mean"), ws=("wrong_side_count", "mean"))
            vio = (vio * 100).sort_values("sj")
            f = go.Figure()
            f.add_bar(y=vio.index, x=vio["sj"], orientation="h", name="Signal jumping", marker_color=C_BAD)
            f.add_bar(y=vio.index, x=vio["ws"], orientation="h", name="Wrong-side driving", marker_color=C_WARN)
            f.update_layout(barmode="group", xaxis_title="Violations per 100 five-minute records")
            show(style(f, 380, "Rule violations by intersection"), "rp_vio")

        cg = RAW.groupby("intersection_name")["green_sec_current"].first()
        odd = cg[cg != 55]
        if len(odd):
            st.info("Note: in the raw data some intersections currently run a different green time than the 55 s used in "
                    "the master dataset — " + ", ".join(f"{k} ({v} s)" for k, v in odd.items()) +
                    ". Use the sidebar's *Current NS/EW green* boxes if you want to compare against those.")


# ============================================================
# TAB 5 — METHODOLOGY
# ============================================================
with tabs[6]:
    st.markdown("### From data to decision: the project pipeline")
    image_if_exists("report_fig7.png", "Project workflow — statistical analysis → forecasting → optimisation → validation")

    steps = [
        ("1 · Traffic demand analysis", "10 intersections compared; ISKCON Cross Road chosen (highest average arrival rate, 3.63 veh/min). "
         "Evening peak is the busiest period; a paired t-test confirms NS (6.90) ≠ EW (6.03) demand."),
        ("2 · Uncertainty estimation", "Mean and standard deviation per phase (NS σ = 2.38, EW σ = 1.84). "
         "420 phase-level observations kept as empirical demand scenarios — no assumed distribution."),
        ("3 · Mathematical optimization", "Split a 110 s green budget between NS and EW with 30–80 s bounds. "
         "Demand-based, uncertainty-adjusted, scenario-based and queue/waiting objectives were compared."),
        ("4 · Optimal green-time allocation", "Queue-and-waiting objective chosen. 55/55 → 56.41/53.59 s; objective 3.9833 → 3.9807 (−0.07%)."),
        ("5 · Rolling next-day forecasting", "Tuesday uses Monday, Wednesday uses Mon–Tue, and so on, per time period, "
         "each with a 95% uncertainty range."),
        ("6 · Validation", "MAE / MAPE / accuracy: weekdays >97% accurate (Thursday 98.26%), weekends noticeably worse."),
        ("7 · Sensitivity analysis", "NS demand ±10% / ±20%: optimal NS green moves consistently with demand while the total stays 110 s."),
    ]
    for t_, body in steps:
        with st.expander(t_):
            st.write(body)

    st.markdown("#### The mathematics")
    m1, m2 = st.columns(2)
    with m1:
        st.latex(r"D^{*} = D_{forecast} + 1.96\,\sigma")
        st.latex(r"\min_{g_{NS},g_{EW}}\; \frac{D^{*}_{NS}}{g_{NS}} + \frac{D^{*}_{EW}}{g_{EW}}")
        st.latex(r"g_{NS}+g_{EW}=110,\quad 30 \le g_{NS},g_{EW} \le 80")
    with m2:
        st.latex(r"\frac{g_{NS}}{g_{EW}}=\sqrt{\frac{D^{*}_{NS}}{D^{*}_{EW}}}")
        st.latex(r"MAPE=\frac{100}{n}\sum\frac{|A-P|}{A},\qquad Accuracy = 100-MAPE")
        st.latex(r"D_{y}=D_{2026}\left(\frac{D_{2036}}{D_{2026}}\right)^{\frac{y-2026}{10}}")
    st.caption("The last formula is how this dashboard interpolates demand between 2026 and 2036 for the year slider.")

    st.markdown("#### How the future-scenario framework is represented")
    show_df(pd.DataFrame({
        "Parameter": ["Vehicle growth", "Vehicle composition", "Traffic demand", "Uncertainty", "Year",
                      "Infrastructure / capacity", "Population / external factors"],
        "What the project studies": ["Registrations & growth rate", "2-wheelers, cars, buses, commercial…",
                                     "Link between vehicles and 2026 traffic", "Variability around future demand",
                                     "2026 → 2030 → 2036", "Demand-to-capacity change", "Only if defensibly linked"],
        "In this dashboard": ["Growth scenario selector (Low / Moderate / High)", "Composition presets + custom sliders (PCU)",
                              "2026 & 2036 demand columns, interpolated by year", "z-score uncertainty margin",
                              "Year / mode selector", "Future work", "Future work"],
    }))

    st.markdown("#### Figures from the report")
    g1, g2 = st.columns(2)
    with g1:
        image_if_exists("report_fig2.png", "Graph 1 — demand by time period")
        image_if_exists("report_fig4.png", "Graph 3 — predicted vs actual demand")
        image_if_exists("report_fig6.png", "Graph 5 — sensitivity of optimal NS green")
    with g2:
        image_if_exists("report_fig3.png", "Graph 2 — NS vs EW demand (evening peak)")
        image_if_exists("report_fig5.png", "Graph 4 — current vs optimized green time")
        image_if_exists("report_fig1.png", "Table — effect of demand variation on optimal green time")

    st.markdown("#### Real-world benefit")
    st.write("Instead of fixed timings, a traffic authority could use the previous days' observations to estimate "
             "tomorrow's demand and automatically assign more green to the heavier phase — reducing unnecessary "
             "waiting and improving signal utilisation, without AI/ML.")
    st.markdown("#### Future scope")
    st.write("Live sensor data · coordinated multi-intersection corridors · weather, incidents, events, pedestrians and "
             "emergency vehicles · objectives for queue length, fuel and emissions · robust / stochastic optimisation.")
    st.warning("Improvement % measures the reduction in the **mathematical objective**, not a guaranteed drop in real-world congestion.")


# ============================================================
# TAB 6 — DATA EXPLORER
# ============================================================
with tabs[7]:
    st.markdown("### Explore the master dataset")
    f1, f2 = st.columns(2)
    pick_i = f1.multiselect("Intersections", INTERSECTIONS, default=INTERSECTIONS)
    pick_v = f2.multiselect("Vehicle scenarios", VS_ORDER, default=VS_ORDER)
    sub = df[df["Intersection"].isin(pick_i) & df["Vehicle Scenario"].isin(pick_v)]
    st.caption(f"{len(sub):,} of {len(df):,} rows")
    show_df(sub.round(3), height=320)
    st.download_button("⬇️ Download filtered data (CSV)", sub.to_csv(index=False).encode("utf-8"),
                       "filtered_traffic_data.csv", "text/csv")

    numeric = [c for c in sub.columns if pd.api.types.is_numeric_dtype(sub[c]) and c != "Scenario ID"]
    if len(sub) > 1 and len(numeric) > 1:
        l, r = st.columns(2, gap="large")
        with l:
            xa = st.selectbox("X axis", numeric, index=numeric.index("NS Demand 2026 (veh/min)")
                              if "NS Demand 2026 (veh/min)" in numeric else 0)
            ya = st.selectbox("Y axis", numeric, index=numeric.index("NS Demand 2036 (veh/min)")
                              if "NS Demand 2036 (veh/min)" in numeric else 1)
            f = px.scatter(sub, x=xa, y=ya, color="Intersection", symbol="Vehicle Scenario")
            show(style(f, 400, f"{ya} vs {xa}"), "ex_scatter")
        with r:
            corr = sub[numeric].corr()
            f = go.Figure(go.Heatmap(z=corr.values, x=corr.columns, y=corr.columns, zmin=-1, zmax=1,
                                     colorscale="RdBu", reversescale=True))
            show(style(f, 480, "Correlation matrix"), "ex_corr")
        bx = st.selectbox("Distribution of…", numeric, index=numeric.index("Traffic Pressure") if "Traffic Pressure" in numeric else 0)
        f = px.box(sub, x="Intersection", y=bx, color="Vehicle Scenario", points="all")
        show(style(f, 420, f"{bx} by intersection and scenario"), "ex_box")

st.markdown("---")
st.caption("Ahmedabad Traffic Optimization · statistics → forecasting → mathematical optimization · "
           "Projected values are scenario-based estimates, not guarantees.")
