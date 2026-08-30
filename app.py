import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(
    page_title="UC Admissions & Socioeconomics Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Creamy Aesthetic & High-Contrast Tab & Typography Styling
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
        margin-bottom: 20px;
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
    
    /* High-Contrast Tab Styling for both Selected and Unselected States */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #F2ECE4;
        border-radius: 10px;
        padding: 10px 20px;
        color: #1A1614 !important;
        border: 1px solid #E5DCD3;
        font-weight: 700;
    }
    .stTabs [data-baseweb="tab"] p {
        color: #1A1614 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1A1614 !important;
        color: #FAF7F2 !important;
    }
    .stTabs [aria-selected="true"] p {
        color: #FAF7F2 !important;
    }

    /* Rounded Styling for Expander Dropdowns */
    div[data-testid="stExpander"] {
        background-color: #FFFFFF;
        border: 1px solid #E8E0D5;
        border-radius: 12px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(46, 39, 36, 0.03);
    }
    div[data-testid="stExpander"] div[role="region"] {
        background-color: #FFFFFF;
        color: #2C221E !important;
        font-size: 1rem !important;
        line-height: 1.6 !important;
        padding: 15px 20px;
        border-bottom-left-radius: 12px;
        border-bottom-right-radius: 12px;
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

# Interactive Tilting Category Cards Component matching your 3 specific tabs
html_cards = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <style>
        body {
            background-color: transparent;
            font-family: 'Inter', -apple-system, sans-serif;
            margin: 0;
            padding: 5px 0 15px 0;
        }
        .container {
            display: flex;
            gap: 20px;
            justify-content: flex-start;
            flex-wrap: wrap;
        }
        .category-card {
            background-color: #FFFFFF;
            border: 1px solid #E8E0D5;
            padding: 18px 16px;
            border-radius: 14px;
            text-align: center;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(46, 39, 36, 0.03);
            width: 260px;
            display: flex;
            align-items: center;
            gap: 15px;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .category-card:hover {
            box-shadow: 0 6px 16px rgba(46, 39, 36, 0.08);
            transform: translateY(-2px);
        }
        .icon-wrapper {
            display: inline-block;
            transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        .icon {
            font-size: 2rem;
            display: block;
        }
        .category-text {
            font-size: 0.95rem;
            font-weight: 700;
            color: #1A1614;
            text-align: left;
            line-height: 1.3;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="category-card" onclick="alert('Visual Analysis & Takeaways selected!')">
            <div class="icon-wrapper"><span class="icon">📊</span></div>
            <div class="category-text">Visual Analysis & Takeaways</div>
        </div>
        <div class="category-card" onclick="alert('School Leaderboards selected!')">
            <div class="icon-wrapper"><span class="icon">📋</span></div>
            <div class="category-text">School Leaderboards</div>
        </div>
        <div class="category-card" onclick="alert('Distribution Overview selected!')">
            <div class="icon-wrapper"><span class="icon">📈</span></div>
            <div class="category-text">Distribution Overview</div>
        </div>
    </div>
    <script>
        const cards = document.querySelectorAll('.category-card');
        cards.forEach(card => {
            const iconWrapper = card.querySelector('.icon-wrapper');
            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const centerX = rect.width / 2;
                const tiltAngle = ((x - centerX) / centerX) * 15;
                iconWrapper.style.transform = `rotate(${tiltAngle}deg) scale(1.15)`;
            });
            card.addEventListener('mouseleave', () => {
                iconWrapper.style.transform = 'rotate(0deg) scale(1)';
            });
        });
    </script>
</body>
</html>
"""
components.html(html_cards, height=100)

# 5. Sidebar Controls (Filtered to exclude years before 2014)
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

    high_rate = round((high_pov["admits"].sum() / high_pov["applicants"].sum() * 100), 2) if high_pov["applicants"].sum() > 0 else 0.00
    low_rate = round((low_pov["admits"].sum() / low_pov["applicants"].sum() * 100), 2) if low_pov["applicants"].sum() > 0 else 0.00
    rate_diff = round(low_rate - high_rate, 2)

    # 7. Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Campus", selected_campus)
    col2.metric(f"High Pov Rate (≥{poverty_threshold}%)", f"{high_rate:.2f}%")
    col3.metric(f"Low Pov Rate (<{poverty_threshold}%)", f"{low_rate:.2f}%")
    col4.metric("Admit Rate Gap", f"{rate_diff:+.2f}%", delta=f"{rate_diff:+.2f}% Gap", delta_color="normal" if rate_diff > 0 else "inverse")

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
                zeroline=True,
                zerolinewidth=1.5,
                zerolinecolor="#1A1614",
                title_font=dict(size=14, color="#1A1614", family="Inter", weight="bold"),
                tickfont=dict(size=12, color="#000000", family="Inter")
            ),
            yaxis=dict(
                showgrid=True, 
                gridcolor="#E5DCD3",
                zeroline=True,
                zerolinewidth=1.5,
                zerolinecolor="#1A1614",
                title_font=dict(size=14, color="#1A1614", family="Inter", weight="bold"),
                tickfont=dict(size=12, color="#000000", family="Inter")
            )
        )
        fig.update_traces(marker=dict(opacity=0.85, line=dict(width=1, color="#FAF7F2")))
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 💡 Deep-Dive Insights (Click to expand)")
        
        with st.expander("📉 Socioeconomic Disparity Breakdown"):
            st.write(f"Schools with lower poverty rates experience an aggregate admit rate of **{low_rate:.2f}%**, compared to **{high_rate:.2f}%** for high-poverty schools (≥{poverty_threshold}% FRPM). This exhibits a clear structural gap in college access across different economic lines.")

        with st.expander("🎯 Regression Trendline Analysis"):
            st.write(f"The downward trendline slope highlights how high school resource density and economic factors systematically correlate with acceptance success into **{selected_campus}**.")

        with st.expander("🏛️ Overall Policy Takeaway"):
            st.write("Targeted intervention and holistic application reviews are vital for bridging the gap and ensuring high-poverty Bay Area schools have equal pathways into top-tier public universities.")

    with tab2:
        st.markdown("### School Performance Breakdowns")
        
        # User-friendly explanation for beginners
        st.markdown("""
        > **How to read these tables:** 
        > * **School Name:** The high school evaluated.
        > * **Poverty Rate (%):** The percentage of students qualifying for Free or Reduced-Price Meals (FRPM).
        > * **Applicants:** Total number of students who applied to this UC campus from the school.
        > * **Admits:** Total number of students accepted.
        > * **Acceptance Rate (%):** The percentage of applicants who received an acceptance letter.
        """)

        col_left, col_right = st.columns(2)

        display_cols = [col for col in ["school_name", "frpm_pct_100", "applicants", "admits", "admit_rate"] if col in filtered.columns]
        rename_map = {
            "school_name": "School Name",
            "frpm_pct_100": "Poverty Rate (%)",
            "applicants": "Applicants",
            "admits": "Admits",
            "admit_rate": "Acceptance Rate (%)"
        }

        with col_left:
            st.markdown("**Highest Poverty High Schools**")
            top_pov = filtered.sort_values(by="frpm_pct_100", ascending=False).head(10)[display_cols].copy()
            top_pov = top_pov.rename(columns=rename_map)
            if "Poverty Rate (%)" in top_pov.columns:
                top_pov["Poverty Rate (%)"] = top_pov["Poverty Rate (%)"].round(2)
            if "Acceptance Rate (%)" in top_pov.columns:
                top_pov["Acceptance Rate (%)"] = top_pov["Acceptance Rate (%)"].round(2)
            st.dataframe(top_pov, hide_index=True, use_container_width=True)

        with col_right:
            st.markdown("**Lowest Poverty High Schools**")
            low_pov_table = filtered.sort_values(by="frpm_pct_100", ascending=True).head(10)[display_cols].copy()
            low_pov_table = low_pov_table.rename(columns=rename_map)
            if "Poverty Rate (%)" in low_pov_table.columns:
                low_pov_table["Poverty Rate (%)"] = low_pov_table["Poverty Rate (%)"].round(2)
            if "Acceptance Rate (%)" in low_pov_table.columns:
                low_pov_table["Acceptance Rate (%)"] = low_pov_table["Acceptance Rate (%)"].round(2)
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
                zeroline=True,
                zerolinewidth=1.5,
                zerolinecolor="#1A1614",
                title_font=dict(size=14, color="#1A1614", family="Inter", weight="bold"),
                tickfont=dict(size=12, color="#000000", family="Inter")
            ),
            yaxis=dict(
                showgrid=True, 
                gridcolor="#E5DCD3",
                zeroline=True,
                zerolinewidth=1.5,
                zerolinecolor="#1A1614",
                title_font=dict(size=14, color="#1A1614", family="Inter", weight="bold"),
                tickfont=dict(size=12, color="#000000", family="Inter")
            )
        )
        st.plotly_chart(fig_hist, use_container_width=True)
