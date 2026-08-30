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

    /* Streamlit Tabs Styling: Vibrant, modern rounded cards with smooth hover */
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

    /* Rounded Styling for Expander Dropdowns */
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

    # 8. Standard Native Streamlit Tabs with custom styling
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Visual Analysis", "📋 School Leaderboards", "📈 Distribution Overview", "🤖 AI Admission Predictor"])

    with tab1:
        st.markdown(f"### Correlation: Poverty vs. Admission Rate ({selected_year})")
        
        fig = px.scatter(
            filtered,
            x="frpm_pct_100",
            y="admit_rate",
            size="applicants",
            color="frpm_pct_100",
            color_continuous_scale=["#93C5FD", "#3B82F6", "#1D4ED8", "#1E3A8A"],
            hover_name="school_name" if "school_name" in filtered.columns else None,
            hover_data=["applicants", "admits"],
            labels={
                "frpm_pct_100": "High School Poverty Rate (% FRPM)",
                "admit_rate": "UC Admit Rate (%)",
                "applicants": "Applicant Volume"
            },
            trendline="ols",
            trendline_color_override="#EF4444"
        )

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#FFFFFF",
            font=dict(color="#0F172A", family="Plus Jakarta Sans", size=12),
            coloraxis_showscale=False,
            height=500,
            margin=dict(t=20, b=20, l=20, r=20),
            xaxis=dict(
                showgrid=True, gridcolor="#F1F5F9", zeroline=True, zerolinewidth=1.5, zerolinecolor="#CBD5E1",
                title_font=dict(size=13, color="#0F172A", family="Plus Jakarta Sans", weight="bold"),
                tickfont=dict(size=12, color="#475569", family="Plus Jakarta Sans")
            ),
            yaxis=dict(
                showgrid=True, gridcolor="#F1F5F9", zeroline=True, zerolinewidth=1.5, zerolinecolor="#CBD5E1",
                title_font=dict(size=13, color="#0F172A", family="Plus Jakarta Sans", weight="bold"),
                tickfont=dict(size=12, color="#475569", family="Plus Jakarta Sans")
            )
        )
        fig.update_traces(marker=dict(opacity=0.85, line=dict(width=1, color="#FFFFFF")))
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 📉 Trend Line: Average Admission Rate Across Poverty Brackets")
        if not filtered.empty:
            filtered["poverty_bin"] = pd.cut(filtered["frpm_pct_100"], bins=10, labels=[f"{i*10}-{(i+1)*10}%" for i in range(10)])
            trend_df = filtered.groupby("poverty_bin", observed=False)["admit_rate"].mean().reset_index()
            
            fig_line1 = px.line(
                trend_df,
                x="poverty_bin",
                y="admit_rate",
                markers=True,
                labels={"poverty_bin": "Poverty Bracket (% FRPM)", "admit_rate": "Average Admit Rate (%)"},
                color_discrete_sequence=["#3B82F6"]
            )
            fig_line1.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="#FFFFFF",
                font=dict(color="#0F172A", family="Plus Jakarta Sans", size=12),
                height=350,
                margin=dict(t=20, b=20, l=20, r=20),
                xaxis=dict(showgrid=True, gridcolor="#F1F5F9", title_font=dict(size=13, weight="bold")),
                yaxis=dict(showgrid=True, gridcolor="#F1F5F9", title_font=dict(size=13, weight="bold"))
            )
            fig_line1.update_traces(line=dict(width=3), marker=dict(size=8))
            st.plotly_chart(fig_line1, use_container_width=True)

        st.markdown("### 💡 Deep-Dive Insights (Click to expand)")
        
        with st.expander("📉 Socioeconomic Disparity Breakdown"):
            st.write(f"Schools with lower poverty rates experience an aggregate admit rate of **{low_rate:.2f}%**, compared to **{high_rate:.2f}%** for high-poverty schools (≥{poverty_threshold}% FRPM). This exhibits a clear structural gap in college access across different economic lines.")

        with st.expander("🎯 Regression Trendline Analysis"):
            st.write(f"The downward trendline slope highlights how high school resource density and economic factors systematically correlate with acceptance success into **{selected_campus}**.")

        with st.expander("🏛️ Overall Policy Takeaway"):
            st.write("Targeted intervention and holistic application reviews are vital for bridging the gap and ensuring high-poverty Bay Area schools have equal pathways into top-tier public universities.")

    with tab2:
        st.markdown("### School Performance Breakdowns")
        
        st.markdown("""
        > **How to read these tables:** > * **School Name:** The high school evaluated.
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

        st.markdown("### 📈 Trend Line: Volume Comparison (Applicants vs. Admits)")
        if not filtered.empty:
            vol_df = filtered.groupby("poverty_bin", observed=False)[["applicants", "admits"]].sum().reset_index()
            vol_melted = vol_df.melt(id_vars="poverty_bin", value_vars=["applicants", "admits"], var_name="Metric", value_name="Total Count")
            
            fig_line2 = px.line(
                vol_melted,
                x="poverty_bin",
                y="Total Count",
                color="Metric",
                markers=True,
                labels={"poverty_bin": "Poverty Bracket (% FRPM)", "Total Count": "Count"},
                color_discrete_map={"applicants": "#3B82F6", "admits": "#10B981"}
            )
            fig_line2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="#FFFFFF",
                font=dict(color="#0F172A", family="Plus Jakarta Sans", size=12),
                height=350,
                margin=dict(t=20, b=20, l=20, r=20),
                xaxis=dict(showgrid=True, gridcolor="#F1F5F9", title_font=dict(size=13, weight="bold")),
                yaxis=dict(showgrid=True, gridcolor="#F1F5F9", title_font=dict(size=13, weight="bold"))
            )
            fig_line2.update_traces(line=dict(width=3), marker=dict(size=8))
            st.plotly_chart(fig_line2, use_container_width=True)

    with tab3:
        st.markdown("### Distribution of Poverty Across Bay Area High Schools")
        fig_hist = px.histogram(
            filtered,
            x="frpm_pct_100",
            nbins=25,
            labels={"frpm_pct_100": "Poverty Rate (% FRPM)", "count": "Number of High Schools"},
            color_discrete_sequence=["#3B82F6"]
        )
        fig_hist.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#FFFFFF",
            font=dict(color="#0F172A", family="Plus Jakarta Sans", size=12),
            height=400,
            xaxis=dict(
                showgrid=True, gridcolor="#F1F5F9", zeroline=True, zerolinewidth=1.5, zerolinecolor="#CBD5E1",
                title_font=dict(size=13, color="#0F172A", family="Plus Jakarta Sans", weight="bold"),
                tickfont=dict(size=12, color="#475569", family="Plus Jakarta Sans")
            ),
            yaxis=dict(
                showgrid=True, gridcolor="#F1F5F9", zeroline=True, zerolinewidth=1.5, zerolinewidth=1.5, zerolinecolor="#CBD5E1",
                title_font=dict(size=13, color="#0F172A", family="Plus Jakarta Sans", weight="bold"),
                tickfont=dict(size=12, color="#475569", family="Plus Jakarta Sans")
            )
        )
        st.plotly_chart(fig_hist, use_container_width=True)

        st.markdown("### 📈 Trend Line: Cumulative High School Distribution")
        if not filtered.empty:
            cum_df = filtered.sort_values("frpm_pct_100").copy()
            cum_df["Cumulative Schools"] = range(1, len(cum_df) + 1)
            
            fig_line3 = px.line(
                cum_df,
                x="frpm_pct_100",
                y="Cumulative Schools",
                labels={"frpm_pct_100": "Poverty Rate (% FRPM)", "Cumulative Schools": "Cumulative Number of Schools"},
                color_discrete_sequence=["#8B5CF6"]
            )
            fig_line3.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="#FFFFFF",
                font=dict(color="#0F172A", family="Plus Jakarta Sans", size=12),
                height=350,
                margin=dict(t=20, b=20, l=20, r=20),
                xaxis=dict(showgrid=True, gridcolor="#F1F5F9", title_font=dict(size=13, weight="bold")),
                yaxis=dict(showgrid=True, gridcolor="#F1F5F9", title_font=dict(size=13, weight="bold"))
            )
            fig_line3.update_traces(line=dict(width=3))
            st.plotly_chart(fig_line3, use_container_width=True)

    with tab4:
        st.markdown("### 🤖 Advanced Machine Learning Admission Predictor")
        st.markdown("Type your high school name to match records, pick your target UC campus, major, and economic details to calculate your predictive admission percentage.")

        col_pred1, col_pred2 = st.columns(2)
        
        all_schools = sorted(df["school_name"].dropna().unique()) if "school_name" in df.columns else []
        
        with col_pred1:
            # Dynamic text search input for high school name
            search_query = st.text_input("Type High School Name (e.g., Berkeley, Lowell, Gunn):", "")
            
            matching_schools = [s for s in all_schools if search_query.lower() in s.lower()] if search_query else all_schools[:50]
            
            selected_school_pred = st.selectbox("Matching High Schools Found:", matching_schools if matching_schools else ["No matches found"])
            
            # Target UC College selection dropdown
            target_uc_college = st.selectbox("Target UC College to Apply To:", campuses)
            
            input_major = st.selectbox("Intended Major Field", ["STEM / Engineering", "Computer Science", "Biological Sciences", "Social Sciences", "Humanities / Arts", "Business / Economics"])

        with col_pred2:
            input_income = st.number_input("Estimated Household Income ($)", min_value=10000, max_value=500000, value=85000, step=5000)
            
            # Pull actual high school data if available, or fallback to manual slider
            school_match_row = df[df["school_name"] == selected_school_pred]
            default_frpm = float(school_match_row["frpm_pct_100"].values[0]) if not school_match_row.empty and "frpm_pct_100" in school_match_row.columns else 35.0
            default_app_vol = int(school_match_row["applicants"].values[0]) if not school_match_row.empty and "applicants" in school_match_row.columns else 50

            input_frpm = st.slider("High School Poverty Rate (% FRPM)", min_value=0.0, max_value=100.0, value=default_frpm, step=1.0)
            input_applicants = st.number_input("Cohort Applicant Volume", min_value=1, max_value=500, value=default_app_vol)

        major_weights = {
            "Computer Science": 0.6,
            "STEM / Engineering": 0.75,
            "Biological Sciences": 0.85,
            "Business / Economics": 0.85,
            "Social Sciences": 1.0,
            "Humanities / Arts": 1.1
        }
        major_multiplier = major_weights.get(input_major, 1.0)

        # Train model specifically based on the target UC college selected
        prediction_target_data = df[df["campus"] == target_uc_college].dropna(subset=["frpm_pct_100", "applicants", "admit_rate"])
        
        if len(prediction_target_data) > 10:
            X = prediction_target_data[["frpm_pct_100", "applicants"]]
            y = prediction_target_data["admit_rate"]
            
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X, y)
            
            base_prediction = model.predict([[input_frpm, input_applicants]])[0]
            final_prediction = base_prediction * major_multiplier
            
            st.write("")
            st.markdown("#### Predicted Outcome:")
            st.metric(label=f"Expected Admit Rate for {target_uc_college} ({input_major})", value=f"{max(0.0, min(100.0, final_prediction)):.2f}%")
            st.info(f"💡 **Simulator Logic:** Evaluates historical trends for **{target_uc_college}** given **{selected_school_pred}'s** poverty profile, adjusted for the competitiveness of **{input_major}**.")
        else:
            st.warning(f"Not enough data points available for **{target_uc_college}** to run the model.")
