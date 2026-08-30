import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(
    page_title="UC Poverty & Admissions Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Creamy Aesthetic CSS Styling
st.markdown("""
    <style>
    /* Main Background & Text Color */
    .stApp {
        background-color: #FAF7F2;
        color: #3C3431;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #F2ECE4;
        border-right: 1px solid #E5DCD3;
    }
    
    /* Custom Metric Cards */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E8E0D5;
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.02);
    }
    
    /* Headings */
    h1, h2, h3, h4 {
        color: #2E2724 !important;
        font-weight: 600;
    }

    /* Target Metric Labels */
    [data-testid="stMetricLabel"] {
        color: #7A6F68 !important;
        font-size: 0.9rem;
    }

    [data-testid="stMetricValue"] {
        color: #2E2724 !important;
        font-weight: 700;
    }

    /* Explanatory Text Box */
    .project-description {
        background-color: #F2ECE4;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #E5DCD3;
        margin-bottom: 25px;
        font-size: 1.05rem;
        line-height: 1.6;
        color: #4A3B32;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Data Loader
@st.cache_data
def load_data():
    df = pd.read_csv("bay_area_modeling_table.csv", low_memory=False)
    
    # Scale FRPM to 0-100% if stored as decimal
    if df["frpm_pct"].max() <= 1.0:
        df["frpm_pct_100"] = df["frpm_pct"] * 100
    else:
        df["frpm_pct_100"] = df["frpm_pct"]
        
    return df

df = load_data()

# 4. Main Question Title & Context Box
st.title("How does student poverty concentration (FRPM) impact UC admission outcomes across Bay Area high schools?")

st.markdown("""
<div class="project-description">
<b>Project Overview:</b> This dashboard explores educational equity across the Bay Area by analyzing how socioeconomic factors shape college access. 
It investigates whether high schools with higher concentrations of students qualifying for Free or Reduced-Price Meals (FRPM) face disparities 
in University of California (UC) acceptance rates, application volumes, and overall institutional access compared to more affluent schools.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# 5. Sidebar Controls
st.sidebar.header("🎛️ Filter Controls")

campuses = sorted(df["campus"].dropna().unique())
default_campus_idx = campuses.index("Universitywide") if "Universitywide" in campuses else 0
selected_campus = st.sidebar.selectbox("Select UC Campus", campuses, index=default_campus_idx)

years = sorted(df["fall_term"].dropna().unique(), reverse=True)
selected_year = st.sidebar.selectbox("Select Fall Term", years, index=0)

poverty_threshold = st.sidebar.slider("High Poverty Threshold (% FRPM)", min_value=10, max_value=90, value=50, step=5)

# 6. Data Filtering
filtered = df[
    (df["fall_term"] == selected_year) & 
    (df["campus"] == selected_campus)
].dropna(subset=["frpm_pct_100", "admits", "applicants"])

filtered["admit_rate"] = (filtered["admits"] / filtered["applicants"]) * 100

high_pov = filtered[filtered["frpm_pct_100"] >= poverty_threshold]
low_pov = filtered[filtered["frpm_pct_100"] < poverty_threshold]

high_rate = (high_pov["admits"].sum() / high_pov["applicants"].sum() * 100) if high_pov["applicants"].sum() > 0 else 0
low_rate = (low_pov["admits"].sum() / low_pov["applicants"].sum() * 100) if low_pov["applicants"].sum() > 0 else 0
rate_diff = low_rate - high_rate

# 7. Key Performance Metrics
m1, m2, m3, m4 = st.columns(4)

m1.metric("Selected Campus", selected_campus)
m2.metric("High Poverty Admit Rate", f"{high_rate:.1f}%", help=f"Schools with ≥{poverty_threshold}% FRPM")
m3.metric("Low Poverty Admit Rate", f"{low_rate:.1f}%", help=f"Schools with <{poverty_threshold}% FRPM")
m4.metric("Admit Rate Gap", f"{rate_diff:+.1f}%", delta=f"{rate_diff:+.1f}% Advantage", delta_color="normal" if rate_diff > 0 else "inverse")

st.write("")

# 8. Plotly Scatter Plot
hover_col = "school_name" if "school_name" in filtered.columns else None

fig = px.scatter(
    filtered,
    x="frpm_pct_100",
    y="admit_rate",
    size="applicants",
    color="frpm_pct_100",
    color_continuous_scale=["#C8B89A", "#8C6D53", "#4A3B32"],
    hover_name=hover_col,
    hover_data=["applicants", "admits"],
    labels={
        "frpm_pct_100": "Poverty Rate (% FRPM)",
        "admit_rate": "UC Admit Rate (%)",
        "applicants": "Total Applicants"
    },
    title=f"High School Poverty Rate vs. Admit Rate ({selected_campus}, {selected_year})",
    trendline="ols",
    trendline_color_override="#2E2724"
)

fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#F2ECE4",
    font=dict(color="#3C3431", family="Arial"),
    coloraxis_showscale=False,
    height=550,
    xaxis=dict(showgrid=True, gridcolor="#E5DCD3", title_font=dict(size=14)),
    yaxis=dict(showgrid=True, gridcolor="#E5DCD3", title_font=dict(size=14))
)

fig.update_traces(marker=dict(opacity=0.85, line=dict(width=1, color="#FAF7F2")))

st.plotly_chart(fig, use_container_width=True)

# 9. Top / Bottom Summary Table
st.markdown("### 📋 School Data Breakdown")
col_left, col_right = st.columns(2)

display_cols = [col for col in ["school_name", "frpm_pct_100", "applicants", "admits", "admit_rate"] if col in filtered.columns]

with col_left:
    st.markdown("**Highest Poverty High Schools**")
    top_pov = filtered.sort_values(by="frpm_pct_100", ascending=False).head(5)[display_cols]
    st.dataframe(top_pov, hide_index=True, use_container_width=True)

with col_right:
    st.markdown("**Lowest Poverty High Schools**")
    low_pov_table = filtered.sort_values(by="frpm_pct_100", ascending=True).head(5)[display_cols]
    st.dataframe(low_pov_table, hide_index=True, use_container_width=True)
