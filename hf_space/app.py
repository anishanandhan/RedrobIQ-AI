import streamlit as st
import pandas as pd
import json
import plotly.express as px
from app.services.scoring import score_candidate
from app.services.reasoning import generate_reasoning
from app.services.honeypot import detect_honeypot

# 1. Page Configuration
st.set_page_config(
    page_title="RedrObIQ Candidate Ranker",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. Theme Toggle State
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"

IS_DARK = st.session_state.theme == "dark"

# 3. CSS Variables and Styling
BG_COLOR = "#09090b" if IS_DARK else "#ffffff"
TEXT_COLOR = "#fafafa" if IS_DARK else "#09090b"
CARD_BG = "#0c0c0f" if IS_DARK else "#ffffff"
BORDER_COLOR = "#1e1e24" if IS_DARK else "#e4e4e7"
GRID_COLOR = "rgba(255,255,255,0.04)" if IS_DARK else "rgba(0,0,0,0.04)"
ACCENT_COLOR = "#2563eb"

# Inject Custom CSS
st.markdown(f"""
<style>
    header[data-testid="stHeader"], #MainMenu, footer, [data-testid="stToolbar"],
    [data-testid="stDecoration"], [data-testid="stStatusWidget"], .stDeployButton,
    div[data-testid="stSidebarCollapsedControl"] {{
        display: none !important;
    }}
    
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .main, .block-container, section[data-testid="stMain"] {{
        background-color: {BG_COLOR} !important;
        color: {TEXT_COLOR} !important;
        font-family: 'DM Sans', -apple-system, sans-serif !important;
    }}
    
    .block-container {{
        padding: 2rem 2.5rem 3rem !important;
        max-width: 1360px !important;
    }}
    
    .brand {{
        margin-bottom: 1.5rem;
    }}
    .brand-name {{
        font-size: 1.6rem;
        font-weight: 700;
        letter-spacing: -0.04em;
        color: {TEXT_COLOR};
    }}
    
    .metric-card {{
        background: {CARD_BG};
        border: 1px solid {BORDER_COLOR};
        border-radius: 10px;
        padding: 1.25rem 1.4rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        margin-bottom: 1rem;
    }}
    .metric-label {{
        font-size: 0.78rem;
        color: #71717a;
        font-weight: 500;
    }}
    .metric-value {{
        font-size: 1.75rem;
        font-weight: 700;
        color: {TEXT_COLOR};
        letter-spacing: -0.03em;
    }}
    
    .chart-wrap {{
        background: {CARD_BG};
        border: 1px solid {BORDER_COLOR};
        border-radius: 10px;
        padding: 1.2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        margin-bottom: 1.5rem;
    }}
    .chart-title {{
        font-size: 0.85rem;
        font-weight: 600;
        color: {TEXT_COLOR};
        margin-bottom: 0.2rem;
    }}
    .chart-subtitle {{
        font-size: 0.72rem;
        color: #a1a1aa;
        margin-bottom: 0.8rem;
    }}
    
    .data-table {{
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        font-size: 0.8rem;
        margin-top: 1rem;
    }}
    .data-table th {{
        text-align: left;
        padding: 0.6rem 0.8rem;
        color: #71717a;
        font-weight: 600;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        border-bottom: 1px solid {BORDER_COLOR};
    }}
    .data-table td {{
        padding: 0.65rem 0.8rem;
        color: {TEXT_COLOR};
        border-bottom: 1px solid #16161a;
    }}
    .data-table tr:hover {{
        background-color: {"#131316" if IS_DARK else "#f4f4f5"};
    }}
    
    .badge {{
        display: inline-block;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.72rem;
        font-weight: 500;
    }}
    .badge-green {{
        color: #22c55e;
        background: rgba(34,197,94,0.12);
    }}
    .badge-red {{
        color: #ef4444;
        background: rgba(239,68,68,0.12);
    }}
    .badge-amber {{
        color: #f59e0b;
        background: rgba(245,158,11,0.12);
    }}
    .badge-blue {{
        color: {ACCENT_COLOR};
        background: rgba(37,99,235,0.1);
    }}
    
    [data-baseweb="tab-list"] {{
        background: {"#0c0c0f" if IS_DARK else "#f9fafb"} !important;
        border: 1px solid {BORDER_COLOR} !important;
        border-radius: 10px !important;
        padding: 3px !important;
    }}
    button[data-baseweb="tab"] {{
        background: transparent !important;
        color: #71717a !important;
        font-size: 0.835rem !important;
        font-weight: 500 !important;
        border-radius: 7px !important;
        border: none !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: {TEXT_COLOR} !important;
        background: {CARD_BG} !important;
        border: 1px solid {BORDER_COLOR} !important;
    }}
</style>
""", unsafe_allow_html=True)

# 4. Helpers for Visual Components
def metric_card(label, value):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color="#71717a" if not IS_DARK else "#a1a1aa", size=11),
    margin=dict(l=10, r=10, t=10, b=10),
    xaxis=dict(
        gridcolor=GRID_COLOR,
        zerolinecolor=GRID_COLOR,
        tickfont=dict(size=10, color="#71717a"),
    ),
    yaxis=dict(
        gridcolor=GRID_COLOR,
        zerolinecolor=GRID_COLOR,
        tickfont=dict(size=10, color="#71717a"),
    ),
)

# 5. Header Component
head_left, head_right = st.columns([8, 1.2])
with head_left:
    st.markdown("""
    <div class="brand">
        <span class="brand-name">◆ RedrObIQ Candidate Ranker</span>
    </div>
    """, unsafe_allow_html=True)
with head_right:
    theme_label = "☀️ Light Mode" if IS_DARK else "🌙 Dark Mode"
    st.button(theme_label, on_click=toggle_theme, use_container_width=True)

# Load Sample Data
@st.cache_data
def load_sample_candidates():
    candidates = []
    with open("sample_candidates.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        for cand in data:
            candidates.append(cand)
    return candidates

try:
    candidates_list = load_sample_candidates()
except Exception:
    candidates_list = []

# Process Candidate Scoring
def score_candidates_df(candidates):
    results = []
    honeypots = []
    for cand in candidates:
        cid = cand.get("candidate_id")
        name = cand.get("profile", {}).get("anonymized_name", "Anonymous")
        location = cand.get("profile", {}).get("location", "Unknown")
        yoe = cand.get("profile", {}).get("years_of_experience", 0)
        notice = cand.get("redrob_signals", {}).get("notice_period_days", 60)
        
        if detect_honeypot(cand):
            honeypots.append({
                "candidate_id": cid,
                "name": name,
                "yoe": yoe,
                "location": location,
                "reason": "Timeline contradiction / Profile anomaly"
            })
            continue
            
        score, breakdown = score_candidate(cand)
        if score > 0:
            reasoning = generate_reasoning(cand, breakdown)
            results.append({
                "candidate_id": cid,
                "name": name,
                "score": score,
                "skill_score": breakdown.get("skill", 0),
                "career_score": breakdown.get("career", 0),
                "behavioral_score": breakdown.get("behavioral", 0),
                "yoe": yoe,
                "location": location,
                "notice_period": notice,
                "reasoning": reasoning
            })
            
    if results:
        df_results = pd.DataFrame(results).sort_values(by=["score", "candidate_id"], ascending=[False, True])
    else:
        df_results = pd.DataFrame(columns=[
            "candidate_id", "name", "score", "skill_score", "career_score",
            "behavioral_score", "yoe", "location", "notice_period", "reasoning"
        ])
        
    if honeypots:
        df_honeypots = pd.DataFrame(honeypots)
    else:
        df_honeypots = pd.DataFrame(columns=["candidate_id", "name", "yoe", "location", "reason"])
        
    return df_results, df_honeypots

df_ranks, df_hps = score_candidates_df(candidates_list)

# Tabs Navigation
tab_shortlist, tab_charts, tab_honeypots, tab_uploader = st.tabs([
    "📋 Shortlist Dashboard", 
    "📊 Visual Analytics", 
    "🛡️ Honeypot Audit", 
    "📥 Real-time Ranker"
])

# --- Tab 1: Shortlist Dashboard ---
with tab_shortlist:
    # KPI Row
    kpi_c1, kpi_c2, kpi_c3 = st.columns(3)
    with kpi_c1:
        metric_card("Total Scanned Profiles", f"{len(candidates_list)}")
    with kpi_c2:
        metric_card("Filtered Honeypots", f"{len(df_hps)}")
    with kpi_c3:
        metric_card("Qualified Shortlist", f"{len(df_ranks)}")
        
    st.markdown("### Top Ranked Candidates")
    st.markdown("<p style='font-size: 0.75rem; color:#71717a;'>Candidates are sorted by composite score descending. Ties are resolved alphabetically by ID ascending.</p>", unsafe_allow_html=True)
    
    # Render table in HTML for premium aesthetics
    table_rows = ""
    for idx, row in df_ranks.head(30).iterrows():
        table_rows += f"""
        <tr>
            <td><b>{row['candidate_id']}</b></td>
            <td>{row['name']}</td>
            <td><span class="badge badge-blue">{row['score']:.4f}</span></td>
            <td>{row['yoe']:.1f} Yrs</td>
            <td>{row['location']}</td>
            <td><span class="badge {'badge-green' if row['notice_period'] <= 30 else ('badge-amber' if row['notice_period'] <= 60 else 'badge-red')}">{row['notice_period']} Days</span></td>
            <td style="max-width: 400px; font-size: 0.75rem;">{row['reasoning']}</td>
        </tr>
        """
    
    st.markdown(f"""
    <div style="overflow-x:auto;">
    <table class="data-table">
        <thead>
            <tr>
                <th>Candidate ID</th>
                <th>Name</th>
                <th>Score</th>
                <th>Experience</th>
                <th>Location</th>
                <th>Notice Period</th>
                <th>Recruiter Summary / Reasoning</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>
    </div>
    """, unsafe_allow_html=True)

# --- Tab 2: Visual Analytics ---
with tab_charts:
    c_left, c_right = st.columns(2)
    
    with c_left:
        st.markdown('<div class="chart-wrap"><div class="chart-title">Skills Fit vs Career Fit</div><div class="chart-subtitle">Scatter mapping showing the core score distribution of candidates.</div>', unsafe_allow_html=True)
        if not df_ranks.empty:
            fig = px.scatter(
                df_ranks, 
                x="skill_score", 
                y="career_score", 
                color="score",
                size="yoe",
                hover_name="name",
                hover_data=["candidate_id", "location"],
                color_continuous_scale="Viridis" if IS_DARK else "Bluered"
            )
            fig.update_layout(**PLOT_LAYOUT)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.write("No data available.")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c_right:
        st.markdown('<div class="chart-wrap"><div class="chart-title">Preferred Hiring Locations</div><div class="chart-subtitle"> Shortlist distribution across key target hubs in India.</div>', unsafe_allow_html=True)
        if not df_ranks.empty:
            loc_counts = df_ranks["location"].value_counts().head(10).reset_index()
            loc_counts.columns = ["Location", "Count"]
            fig_loc = px.bar(
                loc_counts, 
                x="Count", 
                y="Location", 
                orientation="h",
                color_discrete_sequence=[ACCENT_COLOR]
            )
            fig_loc.update_layout(**PLOT_LAYOUT)
            st.plotly_chart(fig_loc, use_container_width=True, config={"displayModeBar": False})
        else:
            st.write("No data available.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="chart-wrap"><div class="chart-title">Notice Period Distribution</div><div class="chart-subtitle">Distribution of notice period intervals (shorter is highly preferred).</div>', unsafe_allow_html=True)
    if not df_ranks.empty:
        fig_notice = px.histogram(
            df_ranks, 
            x="notice_period", 
            nbins=10, 
            color_discrete_sequence=["#f59e0b"]
        )
        fig_notice.update_layout(**PLOT_LAYOUT)
        st.plotly_chart(fig_notice, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

# --- Tab 3: Honeypot Audit ---
with tab_honeypots:
    st.markdown("### Flagged Profile Anomaly Logs")
    st.markdown("<p style='font-size: 0.75rem; color:#71717a;'>These profiles triggered logical filters (such as skill duration > YoE, or single job duration exceeding total career span) and were blocked automatically.</p>", unsafe_allow_html=True)
    
    if not df_hps.empty:
        hp_rows = ""
        for idx, row in df_hps.iterrows():
            hp_rows += f"""
            <tr>
                <td><b>{row['candidate_id']}</b></td>
                <td>{row['name']}</td>
                <td>{row['yoe']:.1f} Yrs</td>
                <td>{row['location']}</td>
                <td><span class="badge badge-red">{row['reason']}</span></td>
            </tr>
            """
        
        st.markdown(f"""
        <table class="data-table">
            <thead>
                <tr>
                    <th>Candidate ID</th>
                    <th>Name</th>
                    <th>Experience</th>
                    <th>Location</th>
                    <th>Disqualification Details</th>
                </tr>
            </thead>
            <tbody>
                {hp_rows}
            </tbody>
        </table>
        """, unsafe_allow_html=True)
    else:
        st.info("No honeypots detected in the loaded dataset.")

# --- Tab 4: Real-time Ranker ---
with tab_uploader:
    st.markdown("### Run Custom Candidate Files")
    st.write("Upload a candidate profile database file (JSONL format) to execute the ranking system and download the shortlist CSV.")
    
    uploaded_file = st.file_uploader("Choose a JSONL candidate file", type=["jsonl", "json"])
    
    if uploaded_file is not None:
        raw_candidates = []
        try:
            # Parse uploads
            if uploaded_file.name.endswith(".jsonl"):
                for line in uploaded_file:
                    line_str = line.decode("utf-8").strip()
                    if line_str:
                        raw_candidates.append(json.loads(line_str))
            else:
                raw_candidates = json.loads(uploaded_file.read().decode("utf-8"))
                
            st.success(f"Successfully loaded {len(raw_candidates)} profiles!")
            
            # Rank candidates
            df_up_ranks, df_up_hps = score_candidates_df(raw_candidates)
            
            # Expose download button
            csv_data = df_up_ranks[["candidate_id", "score", "reasoning"]].copy()
            csv_data.insert(1, "rank", range(1, len(csv_data) + 1))
            csv_str = csv_data.to_csv(index=False)
            
            st.download_button(
                label="📥 Download Shortlist CSV",
                data=csv_str,
                file_name="shortlist_results.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            # Display results
            st.markdown("#### Real-time Shorts")
            st.dataframe(df_up_ranks[["candidate_id", "name", "score", "yoe", "location", "notice_period", "reasoning"]].head(20), use_container_width=True)
            
        except Exception as e:
            st.error(f"Error parsing uploaded file: {e}")
