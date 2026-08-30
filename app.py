import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(
    page_title="UC Admissions & Socioeconomics Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Creamy Aesthetic & High-Contrast Typography Styling (Rounded Modals/Expanders & Icons)
st.markdown("""
    <style>
    .stApp {
        background-color: #FAF7F2;
        color: #1A1614;
        font-family: 'Inter', -apple-system, sans-serif;
    }
    section[data-testid="stSidebar"] {
        background-color: #F2ECE4;
        border-right: 1px solid #E5DCD3;
    }
    
    /* Ensure metric cards have adequate height and no text clipping */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E8E0D5;
        padding: 16px 20px;
        border-radius: 14px;
        box-shadow: 0 4px 12px rgba(46, 39, 36, 0.03);
        min-height: 110px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    h1, h2, h3, h4 {
        color: #1A1614 !important;
        font-weight: 700;
    }
    
    [data-testid="stMetricLabel"] {
        color: #594D47 !important;
        font-size: 0.8rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
        white-space: normal !important;
    }
    [data-testid="stMetricValue"] {
        color: #1A1614 !important;
        font-size: 1.5rem !important;
        font-weight: 800;
        white-space: nowrap;
    }

    .hero-container {
        background-color: #F2ECE4;
        padding: 24px 30px;
        border-radius: 16px;
        border: 1px solid #E5DCD3;
        margin-bottom: 25px;
    }
    .hero-title {
        font-size: 1.6rem;
        font-weight: 800;
        color: #1A1614;
        margin-bottom: 10px;
    }
    .hero-text {
        font-size: 1.05rem;
        line-height: 1.6;
        color: #3C3431;
        margin: 0;
    }
    
    /* Rounded Styling for Expander Dropdowns (Pop-up boxes) */
    .streamlit-expanderHeader {
        background-color: #FFFFFF !important;
        border: 1px solid #E8E0D5 !important;
        border-radius: 12px !important;
        color: #1A1614 !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        padding: 12px 18px !important;
        box-shadow: 0 2px 6px rgba(46, 39, 36, 0.02);
    }
    
    div[data-testid="stExpander"] {
        background-color: #FFFFFF;
        border: 1px solid #E8E0D5;
        border-radius: 12px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(46, 39, 36, 0.03);
    }

    /* Expander Content Readability */
    div[data-testid="stExpander"] div[role="region"] {
        background-color: #FFFFFF;
        color: #2C221E !important;
        font-size: 1rem !important;
        line-height: 1.6 !important;
        padding: 15px 20px;
        border-bottom-left-radius: 12px;
        border-bottom-right-radius: 12px;
    }

    .insight-card {
        background-color: #FFFFFF;
        border: 1px solid #E8E0D5;
        padding: 22px;
        border-radius: 14px;
        box-shadow: 0 4px 12px rgba(46, 39, 36, 0.03);
        margin-bottom: 20px;
    }
    .insight-title {
        font-weight: 700;
        color: #1A1614;
        font-size: 1.1rem;
        margin-bottom: 8px;
    }
    .insight-desc {
        color: #3C3431;
        font-size: 0.95rem;
        line-height: 1.5;
        margin: 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #F2ECE4;
        border-radius: 8px;
        padding: 10px 20px;
        color: #3C3431;
        border: 1px solid #E5DCD3;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1A1614 !important;
        color: #FAF7F2 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Data Loader
@st.cache_data
def load_data():
    df = pd.read_csv("bay_area_modeling_table.csv", low_memory=False)
    if "frpm_pct" in df.columns:
        if df["frpm_pct"].max() <= 1.0:
            df["frpm_pct_100"] = df["frpm_pct"] * 100
        else:
            df["frpm_pct_100"] = df["frpm_pct"]
    return df

df = load_data()

# 4. Hero Section
st.markdown("""
<div class="hero-container">
    <div class="hero-title">How does student poverty concentration (FRPM) impact UC admission outcomes across Bay Area high schools?</div>
    <p class="hero-text">
        This interactive dashboard evaluates structural educational disparities by analyzing how high school socioeconomic status 
        (measured by Free or Reduced-Price Meal eligibility) correlates with University of California acceptance rates, applicant volume, and overall institutional access.
    </p>
</div>
""", unsafe_allow_html=True)

# 5. Sidebar Controls
st.sidebar.header("🎛️ Control Panel")
st.sidebar.markdown("Customize parameters to segment the dataset.")

campuses = sorted(df["campus"].dropna().unique()) if "campus" in df.columns else ["Universitywide"]
default_campus_idx = campuses.index("Universitywide") if "Universitywide" in campuses else 0
selected_campus = st.sidebar.selectbox("Select UC Campus", campuses, index=default_campus_idx)

years = sorted(df["fall_term"].dropna().unique(), reverse=True) if "fall_term" in df.columns else [2025]
selected_year = st.sidebar.selectbox("Select Fall Term", years, index=0)

poverty_threshold = st.sidebar.slider("High Poverty Threshold (% FRPM)", min_value=10, max_value=90, value=50, step=5)

# 6. Data Filtering
filtered = df[
    (df["fall_term"] == selected_year) & 
    (df["campus"] == selected_campus)
].dropna(subset=["frpm_pct_100", "admits", "applicants"]) if "fall_term" in df.columns and "campus" in df.columns else df.copy()

filtered["admit_rate"] = (filtered["admits"] / filtered["applicants"]) * 100

high_pov = filtered[filtered["frpm_pct_100"] >= poverty_threshold]
low_pov = filtered[filtered["frpm_pct_100"] < poverty_threshold]

high_rate = (high_pov["admits"].sum() / high_pov["applicants"].sum() * 100) if high_pov["applicants"].sum() > 0 else 0
low_rate = (low_pov["admits"].sum() / low_pov["applicants"].sum() * 100) if low_pov["applicants"].sum() > 0 else 0
rate_diff = low_rate - high_rate

# 7. Metrics Row
col1, col2, col3, col4 = st.columns(4)
col1.metric("Campus", selected_campus)
col2.metric(f"High Pov Rate (≥{poverty_threshold}%)", f"{high_rate:.1f}%")
col3.metric(f"Low Pov Rate (<{poverty_threshold}%)", f"{low_rate:.1f}%")
col4.metric("Admit Rate Gap", f"{rate_diff:+.1f}%", delta=f"{rate_diff:+.1f}% Gap", delta_color="normal" if rate_diff > 0 else "inverse")

st.write("")

# 8. Main Tabs Layout
tab1, tab2, tab3 = st.tabs(["📊 Visual Analysis & Takeaways", "📋 School Leaderboards", "📈 Distribution Overview"])

with tab1:
    st.markdown(f"### Correlation: Poverty vs. Admission Rate ({selected_year})")
    
    fig = px.scatter(
        filtered,
        x="frpm_pct_100",
        y="admit_rate",
        size="applicants",
        color="frpm_pct_100",
        color_continuous_scale=["#C8B89A", "#8C6D53", "#2C221E"],
        hover_name="school_name" if "school_name" in filtered.columns else None,
        hover_data=["applicants", "admits"],
        labels={
            "frpm_pct_100": "High School Poverty Rate (% FRPM)",
            "admit_rate": "UC Admit Rate (%)",
            "applicants": "Applicant Volume"
        },
        trendline="ols",
        trendline_color_override="#1A1614"
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#F2ECE4",
        font=dict(color="#1A1614", family="Inter", size=12),
        coloraxis_showscale=False,
        height=520,
        margin=dict(t=20, b=20, l=20, r=20),
        xaxis=dict(
            showgrid=True, 
            gridcolor="#E5DCD3",
            title_font=dict(size=14, color="#1A1614", family="Inter"),
            tickfont=dict(size=12, color="#1A1614", family="Inter")
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor="#E5DCD3",
            title_font=dict(size=14, color="#1A1614", family="Inter"),
            tickfont=dict(size=12, color="#1A1614", family="Inter")
        )
    )
    fig.update_traces(marker=dict(opacity=0.85, line=dict(width=1, color="#FAF7F2")))
    st.plotly_chart(fig, use_container_width=True)

    # Interactive Expandable Rounded Cards (Replacing standard blocks with clean clickable pop-ups)
    st.markdown("### 🔍 Deep-Dive Insights (Click to expand)")
    
    with st.expander("📉 Socioeconomic Disparity Breakdown"):
        st.write(f"Schools with lower poverty rates experience an aggregate admit rate of **{low_rate:.1f}%**, compared to **{high_rate:.1f}%** for high-poverty schools (≥{poverty_threshold}% FRPM). This exhibits a clear structural gap in college access across different economic lines.")

    with st.expander("🎯 Regression Trendline Analysis"):
        st.write(f"The downward trendline slope highlights how high school resource density and economic factors systematically correlate with acceptance success into **{selected_campus}**.")

    with st.expander("🏛️ Overall Policy Takeaway"):
        st.write("Targeted intervention and holistic application reviews are vital for bridging the gap and ensuring high-poverty Bay Area schools have equal pathways into top-tier public universities.")

with tab2:
    st.markdown("### School Performance Breakdowns")
    col_left, col_right = st.columns(2)

    display_cols = [col for col in ["school_name", "frpm_pct_100", "applicants", "admits", "admit_rate"] if col in filtered.columns]

    with col_left:
        st.markdown("**Highest Poverty High Schools**")
        top_pov = filtered.sort_values(by="frpm_pct_100", ascending=False).head(10)[display_cols]
        st.dataframe(top_pov, hide_index=True, use_container_width=True)

    with col_right:
        st.markdown("**Lowest Poverty High Schools**")
        low_pov_table = filtered.sort_values(by="frpm_pct_100", ascending=True).head(10)[display_cols]
        st.dataframe(low_pov_table, hide_index=True, use_container_width=True)

with tab3:
    st.markdown("### Distribution of Poverty Across Bay Area High Schools")
    fig_hist = px.histogram(
        filtered,
        x="frpm_pct_100",
        nbins=25,
        labels={"frpm_pct_100": "Poverty Rate (% FRPM)", "count": "Number of High Schools"},
        color_discrete_sequence=["#8C6D53"]
    )
    fig_hist.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#F2ECE4",
        font=dict(color="#1A1614", family="Inter", size=12),
        height=400,
        xaxis=dict(
            showgrid=True, 
            gridcolor="#E5DCD3",
            title_font=dict(size=14, color="#1A1614", family="Inter"),
            tickfont=dict(size=12, color="#1A1614", family="Inter")
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor="#E5DCD3",
            title_font=dict(size=14, color="#1A1614", family="Inter"),
            tickfont=dict(size=12, color="#1A1614", family="Inter")
        )
    )
    st.plotly_chart(fig_hist, use_container_width=True)
