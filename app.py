import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor

# 1. Page Configuration
st.set_page_config(
    page_title="UC Admissions & Socioeconomics Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Vibrant Aesthetic & Modern Typography Styling
st.markdown("""
    <style>
    .stApp {
        background-color: #F8FAFC;
        color: #0F172A;
        font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, sans-serif;
    }
    section[data-testid="stSidebar"] {
        background-color: #EEF2F6;
        border-right: 1px solid #E2E8F0;
    }
    
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        padding: 16px 20px;
        border-radius: 16px;
        box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.05), 0 8px 10px -6px rgba(59, 130, 246, 0.05);
        min-height: 110px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    h1, h2, h3, h4 {
        color: #0F172A !important;
        font-weight: 800;
        letter-spacing: -0.025em;
    }
    
    [data-testid="stMetricLabel"] {
        color: #64748B !important;
        font-size: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 700;
        white-space: normal !important;
    }
    [data-testid="stMetricValue"] {
        color: #2563EB !important;
        font-size: 1.6rem !important;
        font-weight: 900;
        white-space: nowrap;
    }

    .hero-container {
        background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
        padding: 30px 35px;
        border-radius: 20px;
        border: none;
        margin-bottom: 25px;
        box-shadow: 0 20px 25px -5px rgba(37, 99, 235, 0.2);
    }
    .hero-title {
        font-size: 1.7rem;
        font-weight: 900;
        color: #FFFFFF;
        margin-bottom: 12px;
        letter-spacing: -0.02em;
    }
    .hero-text {
        font-size: 1.05rem;
        line-height: 1.6;
        color: #E2E8F0;
        margin: 0;
        font-weight: 400;
    }

    /* Streamlit Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #FFFFFF;
        border-radius: 14px;
        border: 1px solid #E2E8F0;
        padding: 0 24px;
        color: #334155 !important;
        font-weight: 700;
        font-size: 0.95rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #EFF6FF !important;
        color: #2563EB !important;
        border-color: #BFDBFE !important;
        border-radius: 14px !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
        color: #FFFFFF !important;
        border-color: transparent !important;
        border-radius: 14px !important;
        box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3) !important;
    }

    div[data-testid="stExpander"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
    }
    div[data-testid="stExpander"] div[role="region"] {
        background-color: #FFFFFF;
        color: #1E293B !important;
        font-size: 1rem !important;
        line-height: 1.6 !important;
        padding: 20px;
        border-bottom-left-radius: 16px;
        border-bottom-right-radius: 16px;
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

if "fall_term" in df.columns:
    all_years = sorted(df["fall_term"].dropna().unique(), reverse=True)
    years = [y for y in all_years if y >= 2014]
else:
    years = [2025]

selected_year = st.sidebar.selectbox("Select Fall Term", years, index=0)

poverty_threshold = st.sidebar.slider("High Poverty Threshold (% FRPM)", min_value=10, max_value=90, value=50, step=5)

# 6. Data Filtering & Empty Check
filtered = df[
    (df["fall_term"] == selected_year) & 
    (df["campus"] == selected_campus)
].dropna(subset=["frpm_pct_100", "admits", "applicants"]) if "fall_term" in df.columns and "campus" in df.columns else df.copy()

if filtered.empty:
    st.warning(f"⚠️ No data available for **{selected_campus}** in **Fall {selected_year}**. Please select a different year or campus combination from the sidebar.")
else:
    filtered["admit_rate"] = ((filtered["admits"] / filtered["applicants"]) * 100).round(2)
    filtered["frpm_pct_100"] = filtered["frpm_pct_100"].round(2)

    high_pov = filtered[filtered["frpm_pct_100"] >= poverty_threshold]
    low_pov = filtered[filtered["frpm_pct_100"] < poverty_threshold]

    high_rate = round
