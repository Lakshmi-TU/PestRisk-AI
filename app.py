
import sys
import math
from pathlib import Path

import streamlit as st

# ================================================================
# PATHS
# ================================================================
APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

st.set_page_config(
    page_title="PestRisk AI",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ================================================================
# CONSTANTS
# ================================================================
PESTS = [
    "Brown planthopper", "Caseworm", "Gall midge", "Green leafhopper",
    "Leaf folder", "Mirid bug", "White-backed planthopper",
    "Yellow stem borer", "Zig-zag leafhopper",
]

LOCATIONS = [
    "Alappuzha", "Ernakulam", "Idukki", "Kottayam", "Palakkad", "Thrissur",
]

TOPICS = [
    "identification", "symptoms", "favorable_conditions", "monitoring",
    "cultural_control", "biological_control", "mechanical_control",
    "chemical_control", "integrated_pest_management",
]

TOPIC_META = {
    "identification": ("🔍", "Identification"),
    "symptoms": ("🍂", "Symptoms"),
    "favorable_conditions": ("🌦️", "Favorable conditions"),
    "monitoring": ("👁️", "Monitoring"),
    "cultural_control": ("🌾", "Cultural control"),
    "biological_control": ("🐞", "Biological control"),
    "mechanical_control": ("🪤", "Mechanical control"),
    "chemical_control": ("🧪", "Chemical control"),
    "integrated_pest_management": ("♻️", "IPM"),
}

RISK_COLORS = {"Low": "#2e9e5b", "Medium": "#e8a317", "High": "#d64545"}
RISK_ICONS = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}

ATTENTION = {
    "Low": "Predicted risk is low. Routine field observation is appropriate.",
    "Medium": "Predicted risk is moderate. Keep monitoring regular and watch weather trends.",
    "High": "Predicted risk is high. Prioritise field checks and integrated management.",
}

QUICK_QUESTIONS = [
    "What are the symptoms?",
    "How can I monitor this pest?",
    "What conditions favor this pest?",
    "Which natural enemies help?",
    "How do I manage it with IPM?",
]

# ================================================================
# STYLE
# ================================================================
CSS = """
<style>
.block-container {padding-top: 1.1rem; padding-bottom: 3rem; max-width: 1400px;}
#MainMenu, footer {visibility: hidden;}

.hero {background: linear-gradient(120deg,#0f5132 0%,#1b7f4b 55%,#52b06f 100%);
  border-radius: 20px; padding: 26px 34px; color: #fff; display: flex;
  align-items: center; justify-content: space-between; gap: 24px;
  box-shadow: 0 8px 26px rgba(15,81,50,.28); margin-bottom: 18px;}
.hero-title {font-size: 2.2rem; font-weight: 800; letter-spacing: -.5px; line-height: 1.1;}
.hero-sub {margin-top: 8px; font-size: 1.02rem; opacity: .93;}
.hero-badges {display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end;}
.hero-badges span {background: rgba(255,255,255,.16); border: 1px solid rgba(255,255,255,.3);
  padding: 6px 13px; border-radius: 999px; font-size: .82rem; font-weight: 600; white-space: nowrap;}

.sec-title {font-size: 1.25rem; font-weight: 800; color: #12432b; margin: 6px 0 2px;}
.sec-sub {color: #5b6f62; font-size: .9rem; margin-bottom: 10px;}

.card {background: #fff; border: 1px solid #dbe8d8; border-radius: 16px;
  padding: 18px 20px; box-shadow: 0 2px 10px rgba(20,60,35,.06);}
.card h4 {margin: 0 0 10px; font-size: 1.02rem; color: #12432b;}
.card ul {margin: 0; padding-left: 18px;}
.card li {margin-bottom: 8px; line-height: 1.45; color: #26382d;}

.kpi {background: #fff; border: 1px solid #dbe8d8; border-radius: 16px; padding: 14px 18px;
  box-shadow: 0 2px 10px rgba(20,60,35,.06);}
.kpi-label {font-size: .78rem; text-transform: uppercase; letter-spacing: .6px; color: #66796d; font-weight: 700;}
.kpi-value {font-size: 1.55rem; font-weight: 800; margin-top: 4px; line-height: 1.15;}
.kpi-sub {font-size: .8rem; color: #7b8d82; margin-top: 2px;}

.chips {display: flex; flex-wrap: wrap; gap: 8px;}
.chip {background: #eef6ec; border: 1px solid #d5e6d1; border-radius: 12px;
  padding: 8px 12px; font-size: .85rem; color: #1f3a2a;}
.chip b {display: block; font-size: 1.0rem;}
.chip small {color: #66796d;}

.legend {display: flex; gap: 8px; flex-wrap: wrap; margin-top: 8px;}
.legend span {padding: 4px 11px; border-radius: 999px; font-size: .78rem; font-weight: 700; color: #fff;}

.note {border-left: 5px solid; border-radius: 10px; padding: 12px 16px; margin: 10px 0; background: #fff;
  box-shadow: 0 2px 8px rgba(20,60,35,.05);}

.cmp-row {display: grid; grid-template-columns: 190px 1fr 130px; align-items: center; gap: 12px;
  padding: 6px 8px; border-radius: 10px;}
.cmp-row.sel {background: #eef6ec; outline: 1px solid #cfe3ca;}
.cmp-name {font-size: .88rem; font-weight: 600; color: #26382d;}
.cmp-track {background: #edf2ec; border-radius: 999px; height: 12px; overflow: hidden;}
.cmp-fill {height: 100%; border-radius: 999px;}
.cmp-val {font-size: .82rem; font-weight: 700; text-align: right;}

.empty {text-align: center; padding: 46px 20px; color: #5b6f62;}
.empty .big {font-size: 3rem;}

.step {display: flex; gap: 10px; align-items: flex-start; margin-bottom: 9px; font-size: .88rem; color: #26382d;}
.step .n {background: #1b7f4b; color: #fff; border-radius: 50%; min-width: 22px; height: 22px;
  display: flex; align-items: center; justify-content: center; font-size: .75rem; font-weight: 700;}

div.stButton > button {border-radius: 12px; font-weight: 700;}
div[data-testid="stTabs"] button[role="tab"] {font-weight: 700; font-size: 1rem;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ================================================================
# BACKEND LOADERS (same engines as before)
# ================================================================
@st.cache_resource(show_spinner="Loading ML model...")
def load_ml():
    import ml_engine
    ml_engine.load_artifacts()
    return ml_engine


@st.cache_resource(show_spinner="Loading knowledge base...")
def load_rag_bundle():
    import rag_engine
    return rag_engine, rag_engine.load_rag()


@st.cache_resource(show_spinner="Loading Q&A engine (first time can take a while)...")
def load_qna():
    import qna_engine
    return qna_engine


ml_engine = load_ml()
rag_engine, rag = load_rag_bundle()

try:
    LOW_T, HIGH_T = ml_engine.get_thresholds()
except Exception:
    LOW_T, HIGH_T = 0.50, 0.70

# ================================================================
# SESSION STATE
# ================================================================
if "result" not in st.session_state:
    st.session_state.result = None
if "chat" not in st.session_state:
    st.session_state.chat = []
if "pending_q" not in st.session_state:
    st.session_state.pending_q = None

# ================================================================
# HELPERS
# ================================================================
def kpi(label, value, sub="", color="#1b7f4b", icon=""):
    return (
        f'<div class="kpi" style="border-top:4px solid {color}">'
        f'<div class="kpi-label">{icon} {label}</div>'
        f'<div class="kpi-value" style="color:{color}">{value}</div>'
        f'<div class="kpi-sub">{sub}</div></div>'
    )


def section(title, sub=""):
    st.markdown(
        f'<div class="sec-title">{title}</div><div class="sec-sub">{sub}</div>',
        unsafe_allow_html=True,
    )


def gauge_svg(p, low, high, color):
    cx, cy, r = 150, 150, 110

    def pt(v, rad=r):
        th = math.pi * (1 - v)
        return cx + rad * math.cos(th), cy - rad * math.sin(th)

    def arc(a, b, col):
        x1, y1 = pt(a)
        x2, y2 = pt(b)
        return (
            f'<path d="M {x1:.1f} {y1:.1f} A {r} {r} 0 0 1 {x2:.1f} {y2:.1f}" '
            f'stroke="{col}" stroke-width="22" fill="none"/>'
        )

    nx, ny = pt(p, r - 28)
    tl_x, tl_y = pt(low, r + 20)
    th_x, th_y = pt(high, r + 20)
    parts = [
        '<svg viewBox="0 0 300 200" width="100%" style="max-width:420px">',
        arc(0.0, low, RISK_COLORS["Low"]),
        arc(low, high, RISK_COLORS["Medium"]),
        arc(high, 1.0, RISK_COLORS["High"]),
        f'<line x1="{cx}" y1="{cy}" x2="{nx:.1f}" y2="{ny:.1f}" stroke="#1c2b22" stroke-width="4" stroke-linecap="round"/>',
        f'<circle cx="{cx}" cy="{cy}" r="9" fill="#1c2b22"/>',
        f'<text x="{tl_x:.1f}" y="{tl_y:.1f}" font-size="10" text-anchor="middle" fill="#66796d">{low:.2f}</text>',
        f'<text x="{th_x:.1f}" y="{th_y:.1f}" font-size="10" text-anchor="middle" fill="#66796d">{high:.2f}</text>',
        '<text x="34" y="172" font-size="10" fill="#66796d">0</text>',
        '<text x="256" y="172" font-size="10" fill="#66796d">1</text>',
        f'<text x="{cx}" y="190" font-size="26" font-weight="800" text-anchor="middle" fill="{color}">{p*100:.1f}%</text>',
        '</svg>',
    ]
    return "".join(parts)


def extract_sources(meta):
    out = []
    if isinstance(meta, dict):
        for s in meta.get("sources", []) or []:
            if isinstance(s, dict):
                title = str(s.get("title", "")).strip()
                org = str(s.get("organization", "")).strip()
                url = str(s.get("url", "")).strip()
                if title or org:
                    out.append((title, org, url))
    return out


def build_advisory(pest, ml_result, rag_result):
    by_topic = {i["topic"]: i for i in rag_result.get("results", [])}
    obs, actions, avoid = [], [], []

    if "favorable_conditions" in by_topic:
        obs.append(f"Validated information describes the conditions associated with {pest} in rice.")
    if "monitoring" in by_topic:
        obs.append(f"Regular field monitoring is supported for {pest} management.")
    if "symptoms" in by_topic:
        obs.append(f"Symptom guidance is available for {pest}; compare it with what you see in the field.")

    if "cultural_control" in by_topic:
        actions.append(f"Follow validated cultural-management practices for {pest}.")
    if "biological_control" in by_topic:
        actions.append(f"Conserve or use validated biological-control approaches for {pest}.")
    if "mechanical_control" in by_topic:
        actions.append(f"Use validated physical or mechanical practices where appropriate for {pest}.")
    if "monitoring" in by_topic:
        actions.append(f"Monitor the crop regularly using the validated guidance for {pest}.")
    if "integrated_pest_management" in by_topic:
        actions.append(f"Base decisions on field observations and validated IPM guidance for {pest}.")

    if "chemical_control" in by_topic:
        avoid.append(
            "Avoid unnecessary or broad-spectrum pesticide use unless intervention is "
            "supported by validated field evidence and guidance."
        )

    return {"observations": obs, "actions": actions, "avoid": avoid}


def li(items):
    if not items:
        return "<ul><li>No validated guidance available for this section.</li></ul>"
    return "<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>"


def run_question(question, pest):
    qna = load_qna()
    hist = st.session_state.chat
    ctx = "\n".join(f'{m["role"]}: {m["content"]}' for m in hist[-4:])
    out = qna.ask_pestrisk(question, selected_pest=pest, conversation_context=ctx)
    hist.append({"role": "Farmer", "content": question})
    hist.append({
        "role": "PestRisk AI",
        "content": out.get("answer", ""),
        "pest": out.get("pest"),
        "evidence": out.get("evidence", []),
        "status": out.get("status"),
    })


def queue_question(q):
    st.session_state.pending_q = q


# ================================================================
# HERO
# ================================================================
st.markdown(
    """
<div class="hero">
  <div>
    <div class="hero-title">🌾 PestRisk AI</div>
    <div class="hero-sub">Weather-based rice pest risk prediction &amp; sustainable IPM advisory</div>
  </div>
  <div class="hero-badges">
    <span>🤖 Calibrated ML model</span>
    <span>📚 Validated evidence (RAG)</span>
    <span>🛡️ Grounded advice</span>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# ================================================================
# SIDEBAR
# ================================================================
with st.sidebar:
    st.markdown("### 🌾 PestRisk AI")
    st.markdown(
        """
<div class="step"><div class="n">1</div><div>Enter field &amp; weather conditions</div></div>
<div class="step"><div class="n">2</div><div>ML model predicts observation risk</div></div>
<div class="step"><div class="n">3</div><div>Validated evidence is retrieved</div></div>
<div class="step"><div class="n">4</div><div>Farmer advisory &amp; Q&amp;A</div></div>
""",
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown("**Risk bands**")
    st.markdown(
        f'<div class="legend">'
        f'<span style="background:{RISK_COLORS["Low"]}">Low &lt; {LOW_T:.2f}</span>'
        f'<span style="background:{RISK_COLORS["Medium"]}">Medium {LOW_T:.2f}–{HIGH_T:.2f}</span>'
        f'<span style="background:{RISK_COLORS["High"]}">High ≥ {HIGH_T:.2f}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.divider()
    usable = rag.get("usable_chunks", rag.get("chunks", []))
    st.caption(f"🤖 ML model: ready")
    st.caption(f"📚 Knowledge base: {len(usable)} validated chunks")
    st.divider()
    if st.button("♻️ Reset dashboard", use_container_width=True):
        st.session_state.result = None
        st.session_state.chat = []
        st.session_state.pending_q = None
        st.rerun()
    st.caption(
        "The predicted observation risk does not by itself confirm pest infestation."
    )

# ================================================================
# INPUT PANEL (horizontal)
# ================================================================
section("📝 Field & Weather Inputs", "Set the pest, location and current weather, then run the prediction.")

c1, c2, c3 = st.columns(3)

with c1:
    with st.container(border=True):
        st.markdown("**🐛 Pest & Place**")
        pest_name = st.selectbox("Pest", PESTS, key="pest_sel")
        location = st.selectbox("Location", LOCATIONS, key="loc_sel")
        standard_week = st.number_input("Standard week", 1, 53, 30, 1)

with c2:
    with st.container(border=True):
        st.markdown("**🌡️ Temperature & Humidity**")
        t1, t2 = st.columns(2)
        with t1:
            max_temp = st.number_input("Max temp (°C)", -10.0, 60.0, 32.0, 0.1)
        with t2:
            min_temp = st.number_input("Min temp (°C)", -10.0, 60.0, 25.0, 0.1)
        h1, h2 = st.columns(2)
        with h1:
            rh1 = st.number_input("RH 1 (%)", 0.0, 100.0, 80.0, 0.1)
        with h2:
            rh2 = st.number_input("RH 2 (%)", 0.0, 100.0, 75.0, 0.1)

with c3:
    with st.container(border=True):
        st.markdown("**🌧️ Rain, Wind & Sun**")
        r1, r2 = st.columns(2)
        with r1:
            rainfall = st.number_input("Rainfall (mm)", 0.0, 1000.0, 10.0, 0.1)
        with r2:
            wind_speed = st.number_input("Wind (km/h)", 0.0, 200.0, 8.0, 0.1)
        s1, s2 = st.columns(2)
        with s1:
            sunshine = st.number_input("Sunshine (hrs)", 0.0, 24.0, 6.0, 0.1)
        with s2:
            evaporation = st.number_input("Evaporation (mm)", 0.0, 100.0, 4.0, 0.1)

if min_temp > max_temp:
    st.warning("Minimum temperature is higher than maximum temperature. Please check the values.")

predict_clicked = st.button("🔍 Predict Pest Risk", type="primary", use_container_width=True)

# ================================================================
# PREDICTION
# ================================================================
if predict_clicked:
    inputs = dict(
        standard_week=standard_week, max_temp=max_temp, min_temp=min_temp,
        rh1=rh1, rh2=rh2, rainfall=rainfall, wind_speed=wind_speed,
        sunshine=sunshine, evaporation=evaporation,
        pest_name=pest_name, location=location,
    )
    try:
        with st.spinner("Running ML prediction and retrieving validated evidence..."):
            ml_result = ml_engine.predict_risk(**inputs)

            rag_result = rag_engine.retrieve_topic_evidence_explicit(
                rag=rag, pest=pest_name, topics=TOPICS, top_k_per_topic=1,
            )

            advisory = build_advisory(pest_name, ml_result, rag_result)

            compare = []
            for p in PESTS:
                try:
                    r = ml_engine.predict_risk(**{**inputs, "pest_name": p})
                    compare.append((p, float(r["predicted_observation_risk"]), r["risk_level"]))
                except Exception:
                    pass

        st.session_state.result = {
            "inputs": inputs, "ml": ml_result, "rag": rag_result,
            "advisory": advisory, "compare": compare,
        }
    except Exception as e:
        st.error("Prediction failed. Please check the inputs and the application log.")
        st.exception(e)

# ================================================================
# TABS
# ================================================================
tab_risk, tab_adv, tab_evd, tab_qa = st.tabs(
    ["📊 Risk Assessment", "🌱 Advisory", "📚 Evidence", "💬 Ask PestRisk AI"]
)

res = st.session_state.result


def empty_state():
    st.markdown(
        '<div class="card empty"><div class="big">🌾</div>'
        '<div><b>No prediction yet</b></div>'
        '<div>Fill in the inputs above and click <b>Predict Pest Risk</b>.</div></div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------
# TAB 1 — RISK
# ---------------------------------------------------------------
with tab_risk:
    if res is None:
        empty_state()
    else:
        ml = res["ml"]
        inp = res["inputs"]
        prob = float(ml["predicted_observation_risk"])
        level = ml["risk_level"]
        color = RISK_COLORS.get(level, "#1b7f4b")

        k1, k2, k3, k4 = st.columns(4)
        k1.markdown(kpi("Pest", ml["pest"], "Selected pest", "#1b7f4b", "🐛"), unsafe_allow_html=True)
        k2.markdown(kpi("Location", ml["location"], f'Standard week {inp["standard_week"]}', "#1b7f4b", "📍"), unsafe_allow_html=True)
        k3.markdown(kpi("Risk level", f'{RISK_ICONS.get(level, "")} {level}', "Predicted observation risk", color, "⚠️"), unsafe_allow_html=True)
        k4.markdown(kpi("Probability", f"{prob*100:.1f}%", f"Raw score {prob:.6f}", color, "📈"), unsafe_allow_html=True)

        st.write("")
        g1, g2 = st.columns([1, 1.25])

        with g1:
            st.markdown(
                '<div class="card" style="text-align:center"><h4>Risk gauge</h4>'
                + gauge_svg(prob, LOW_T, HIGH_T, color)
                + '<div class="legend" style="justify-content:center">'
                + f'<span style="background:{RISK_COLORS["Low"]}">Low</span>'
                + f'<span style="background:{RISK_COLORS["Medium"]}">Medium</span>'
                + f'<span style="background:{RISK_COLORS["High"]}">High</span>'
                + '</div></div>',
                unsafe_allow_html=True,
            )

        with g2:
            chips = [
                ("🌡️", "Temperature", f'{inp["min_temp"]:.1f}–{inp["max_temp"]:.1f} °C'),
                ("💧", "Humidity", f'{inp["rh1"]:.0f}% / {inp["rh2"]:.0f}%'),
                ("🌧️", "Rainfall", f'{inp["rainfall"]:.1f} mm'),
                ("💨", "Wind", f'{inp["wind_speed"]:.1f} km/h'),
                ("☀️", "Sunshine", f'{inp["sunshine"]:.1f} hrs'),
                ("♨️", "Evaporation", f'{inp["evaporation"]:.1f} mm'),
            ]
            chip_html = "".join(
                f'<div class="chip"><small>{i} {l}</small><b>{v}</b></div>' for i, l, v in chips
            )
            st.markdown(
                f'<div class="card"><h4>Interpretation</h4>'
                f'<div class="note" style="border-color:{color}">{ml["interpretation"]}</div>'
                f'<div class="note" style="border-color:#1b7f4b">{ATTENTION.get(level, "")}</div>'
                f'<h4 style="margin-top:14px">Weather snapshot</h4>'
                f'<div class="chips">{chip_html}</div></div>',
                unsafe_allow_html=True,
            )

        if res["compare"]:
            st.write("")
            rows = ""
            for p, pr, lvl in sorted(res["compare"], key=lambda x: -x[1]):
                c = RISK_COLORS.get(lvl, "#1b7f4b")
                sel = " sel" if p == ml["pest"] else ""
                rows += (
                    f'<div class="cmp-row{sel}"><div class="cmp-name">{p}</div>'
                    f'<div class="cmp-track"><div class="cmp-fill" style="width:{pr*100:.1f}%;background:{c}"></div></div>'
                    f'<div class="cmp-val" style="color:{c}">{pr*100:.1f}% · {lvl}</div></div>'
                )
            st.markdown(
                f'<div class="card"><h4>All pests at these conditions</h4>'
                f'<div class="sec-sub">Same weather, week and location; only the pest changes.</div>{rows}</div>',
                unsafe_allow_html=True,
            )

# ---------------------------------------------------------------
# TAB 2 — ADVISORY
# ---------------------------------------------------------------
with tab_adv:
    if res is None:
        empty_state()
    else:
        adv = res["advisory"]
        a1, a2, a3 = st.columns(3)
        a1.markdown(f'<div class="card"><h4>📌 Key observations</h4>{li(adv["observations"])}</div>', unsafe_allow_html=True)
        a2.markdown(f'<div class="card"><h4>🌱 Recommended actions</h4>{li(adv["actions"])}</div>', unsafe_allow_html=True)
        a3.markdown(f'<div class="card" style="border-color:#efc9c9"><h4>🚫 What to avoid</h4>{li(adv["avoid"])}</div>', unsafe_allow_html=True)

        st.write("")
        st.markdown(
            '<div class="card"><h4>ℹ️ Important information</h4><ul>'
            '<li>This advisory is based on validated rice-pest information available for this assessment.</li>'
            '<li>The predicted observation risk does not by itself confirm pest infestation.</li>'
            '<li>Specific chemical treatment details are not provided unless directly supported by validated evidence.</li>'
            '</ul></div>',
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------
# TAB 3 — EVIDENCE
# ---------------------------------------------------------------
with tab_evd:
    if res is None:
        empty_state()
    else:
        rr = res["rag"]
        results = rr.get("results", [])
        cov = rr.get("coverage", {})
        missing = cov.get("missing", [])

        e1, e2, e3 = st.columns(3)
        e1.markdown(kpi("Topics requested", cov.get("requested", len(TOPICS)), "", "#1b7f4b", "🗂️"), unsafe_allow_html=True)
        e2.markdown(kpi("Topics retrieved", cov.get("retrieved", len(results)), "", "#2e9e5b", "✅"), unsafe_allow_html=True)
        e3.markdown(kpi("Not available", len(missing), "No validated source", "#e8a317" if missing else "#2e9e5b", "⚠️"), unsafe_allow_html=True)

        if missing:
            names = ", ".join(TOPIC_META.get(m, ("", m))[1] for m in missing)
            st.info(f"Validated evidence is not available for: {names}.")

        st.write("")
        by_topic = {r["topic"]: r for r in results}
        ordered = [t for t in TOPICS if t in by_topic]

        if ordered:
            labels = [f'{TOPIC_META[t][0]} {TOPIC_META[t][1]}' for t in ordered]
            tabs = st.tabs(labels)
            for t, tb in zip(ordered, tabs):
                with tb:
                    item = by_topic[t]
                    st.markdown(
                        f'<div class="card"><h4>{TOPIC_META[t][0]} {TOPIC_META[t][1]} — {res["ml"]["pest"]}</h4>'
                        f'<div style="line-height:1.6;color:#26382d">{str(item.get("text", "")).strip()}</div></div>',
                        unsafe_allow_html=True,
                    )
                    srcs = extract_sources(item.get("source_metadata", {}))
                    if srcs:
                        st.caption("Sources")
                        for title, org, url in srcs:
                            label = title or org
                            label = f"{label} — {org}" if (title and org) else label
                            st.markdown(f"- [{label}]({url})" if url else f"- {label}")

# ---------------------------------------------------------------
# TAB 4 — ASK PESTRISK AI
# ---------------------------------------------------------------
with tab_qa:
    section("💬 Ask PestRisk AI", "Answers are prepared only from validated rice-pest information.")

    qa_pest = res["ml"]["pest"] if res else st.session_state.get("pest_sel", PESTS[0])
    st.caption(f"Answering about: **{qa_pest}** (mention another pest in your question to switch)")

    qcols = st.columns(len(QUICK_QUESTIONS))
    for col, q in zip(qcols, QUICK_QUESTIONS):
        col.button(q, key=f"quick_{q}", on_click=queue_question, args=(q,), use_container_width=True)

    with st.form("qna_form", clear_on_submit=True):
        f1, f2 = st.columns([5, 1])
        typed = f1.text_input(
            "Your question",
            placeholder="e.g. What are the symptoms of brown planthopper?",
            label_visibility="collapsed",
        )
        sent = f2.form_submit_button("Ask 🤖", use_container_width=True, type="primary")

    if sent and typed.strip():
        st.session_state.pending_q = typed.strip()

    if st.session_state.pending_q:
        q = st.session_state.pending_q
        st.session_state.pending_q = None
        try:
            with st.spinner("Searching validated information and preparing your answer..."):
                run_question(q, qa_pest)
        except Exception as e:
            st.error("The Q&A service could not complete the request.")
            st.caption(f"{type(e).__name__}: {e}")

    hist = st.session_state.chat
    if hist:
        head, clear_col = st.columns([5, 1])
        head.markdown("**Conversation**")
        if clear_col.button("🗑️ Clear", use_container_width=True):
            st.session_state.chat = []
            st.rerun()

        for m in hist:
            if m["role"] == "Farmer":
                with st.chat_message("user"):
                    st.write(m["content"])
            else:
                with st.chat_message("assistant"):
                    st.write(m["content"])
                    if m.get("pest"):
                        st.caption(f'Pest context: {m["pest"]}')
                    ev = m.get("evidence") or []
                    if ev:
                        with st.expander("📚 Evidence used for this answer"):
                            shown = set()
                            for item in ev:
                                topic = str(item.get("topic", "Validated information"))
                                text = str(item.get("text", "")).strip()
                                if not text or topic in shown:
                                    continue
                                shown.add(topic)
                                st.markdown(f'**{topic.replace("_", " ").title()}**')
                                st.write(text)
                    elif m.get("status") == "UNKNOWN_PEST":
                        st.caption("This question referred to a pest outside the validated knowledge base.")
    else:
        st.markdown(
            '<div class="card empty"><div class="big">💬</div>'
            '<div><b>Ask your first question</b></div>'
            '<div>Use a quick question above or type your own.</div></div>',
            unsafe_allow_html=True,
        )

# ================================================================
# FOOTER
# ================================================================
st.write("")
st.caption(
    "PestRisk AI • Weather-based rice pest risk prediction and sustainable "
    "integrated pest management advisory"
)
