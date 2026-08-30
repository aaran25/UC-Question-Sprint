import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression

# 1. Page Configuration
st.set_page_config(
    page_title="UC Admissions & Socioeconomics Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Futuristic Utopian Sci-Fi Theme & Hover-Tilt Styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');

    .stApp {
        background-color: #0B0F17;
        color: #F8FAFC;
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
    }
    
    section[data-testid="stSidebar"] {
        background-color: #0F172A;
        border-right: 1px solid #1E293B;
    }
    
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(56, 189, 248, 0.2);
        padding: 16px 20px;
        border-radius: 16px;
        box-shadow: 0 10px 30px -10px rgba(56, 189, 248, 0.15);
        min-height: 110px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: all 0.3s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        border-color: rgba(56, 189, 248, 0.6);
        box-shadow: 0 15px 35px -5px rgba(56, 189, 248, 0.3);
    }
    
    h1, h2, h3, h4 {
        color: #F8FAFC !important;
        font-weight: 800;
        letter-spacing: -0.025em;
    }
    
    [data-testid="stMetricLabel"] {
        color: #94A3B8 !important;
        font-size: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 700;
    }
    [data-testid="stMetricValue"] {
        color: #38BDF8 !important;
        font-size: 1.6rem !important;
        font-weight: 900;
        text-shadow: 0 0 15px rgba(56, 189, 248, 0.4);
    }

    .hero-container {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(6, 78, 59, 0.4) 100%), 
                    radial-gradient(circle at top right, rgba(56, 189, 248, 0.15), transparent 50%);
        padding: 35px 40px;
        border-radius: 20px;
        border: 1px solid rgba(56, 189, 248, 0.3);
        margin-bottom: 25px;
        box-shadow: 0 20px 40px -15px rgba(56, 189, 248, 0.2);
        backdrop-filter: blur(10px);
    }
    .hero-title {
        font-size: 1.8rem;
        font-weight: 900;
        color: #FFFFFF;
        margin-bottom: 12px;
        letter-spacing: -0.02em;
        text-shadow: 0 0 20px rgba(56, 189, 248, 0.5);
    }
    .hero-text {
        font-size: 1.05rem;
        line-height: 1.6;
        color: #94A3B8;
        margin: 0;
    }

    .analysis-box {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(56, 189, 248, 0.3);
        padding: 20px 24px;
        border-radius: 16px;
        margin-top: 20px;
        box-shadow: 0 10px 25px -5px rgba(56, 189, 248, 0.1);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #0F172A;
        border-radius: 14px;
        border: 1px solid rgba(56, 189, 248, 0.2);
        padding: 0 20px;
        color: #94A3B8 !important;
        font-weight: 700;
        font-size: 0.9rem;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #1E293B !important;
        color: #38BDF8 !important;
        border-color: rgba(56, 189, 248, 0.5) !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0ea5e9 0%, #0369a1 100%) !important;
        color: #FFFFFF !important;
        border-color: transparent !important;
        box-shadow: 0 10px 20px -3px rgba(14, 165, 233, 0.4) !important;
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
    <div class="hero-title">🌐 Utopian Core: UC Admissions Matrix</div>
    <p class="hero-text">
        Advanced telemetry tracking student socioeconomic dynamics, poverty concentrations (FRPM), and institutional access across Bay Area educational sectors.
    </p>
</div>
""", unsafe_allow_html=True)

# 5. Sidebar Controls
st.sidebar.header("🎛️ System Controls")
st.sidebar.markdown("Configure core parameter vectors.")

campuses = sorted(df["campus"].dropna().unique()) if "campus" in df.columns else ["Universitywide"]
default_campus_idx = campuses.index("Universitywide") if "Universitywide" in campuses else 0
selected_campus = st.sidebar.selectbox("🏛️ Target UC Campus", campuses, index=default_campus_idx)

if "fall_term" in df.columns:
    all_years = sorted(df["fall_term"].dropna().unique(), reverse=True)
    years = [y for y in all_years if y >= 2014]
else:
    years = [2025]

selected_year = st.sidebar.selectbox("📅 Temporal Cycle (Fall Term)", years, index=0)
poverty_threshold = 50.0

# 6. Data Filtering & Empty Check
filtered = df[
    (df["fall_term"] == selected_year) & 
    (df["campus"] == selected_campus)
].dropna(subset=["frpm_pct_100", "admits", "applicants"]) if "fall_term" in df.columns and "campus" in df.columns else df.copy()

if filtered.empty:
    st.warning(f"⚠️ Zero telemetry found for **{selected_campus}** during **Fall {selected_year}**.")
else:
    filtered["admit_rate"] = ((filtered["admits"] / filtered["applicants"]) * 100).round(2)
    filtered["frpm_pct_100"] = filtered["frpm_pct_100"].round(2)

    high_pov = filtered[filtered["frpm_pct_100"] >= poverty_threshold]
    low_pov = filtered[filtered["frpm_pct_100"] < poverty_threshold]

    high_rate = round((high_pov["admits"].sum() / high_pov["applicants"].sum() * 100), 2) if high_pov["applicants"].sum() > 0 else 0.00
    low_rate = round((low_pov["admits"].sum() / low_pov["applicants"].sum() * 100), 2) if low_pov["applicants"].sum() > 0 else 0.00
    rate_diff = round(low_rate - high_rate, 2)

    # Opportunity Gap Ratio calculation
    opp_gap_ratio = round(low_rate / high_rate, 2) if high_rate > 0 else 0.00

    # 7. Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🏛️ Active Node", selected_campus)
    col2.metric("📈 High Pov Yield (≥50%)", f"{high_rate:.2f}%")
    col3.metric("📉 Low Pov Yield (<50%)", f"{low_rate:.2f}%")
    col4.metric("⚖️ Opportunity Gap Ratio", f"{opp_gap_ratio}x", delta=f"{rate_diff:+.2f}% Gap", delta_color="normal" if rate_diff > 0 else "inverse")

    st.write("")

    # 8. Tabs (Added Equity & Opportunity Gap Tab)
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Visual Telemetry", 
        "⚖️ Equity & Opportunity Gap", 
        "📋 Sector Leaderboards", 
        "📈 Demographic Spectrum", 
        "🤖 Neural Predictor Matrix"
    ])

    with tab1:
        st.markdown(f"### 🔍 Telemetry Grid: Socioeconomic Impact vs. Success Rate ({selected_year})")
        
        fig = px.scatter(
            filtered,
            x="frpm_pct_100",
            y="admit_rate",
            size="applicants",
            color="frpm_pct_100",
            color_continuous_scale=["#38BDF8", "#0284C7", "#0369A1", "#0F172A"],
            hover_name="high_school" if "high_school" in filtered.columns else None,
            hover_data=["applicants", "admits"],
            labels={
                "frpm_pct_100": "High School Poverty Rate (% FRPM)",
                "admit_rate": "UC Admit Rate (%)",
                "applicants": "Applicant Volume"
            },
            trendline="ols",
            trendline_color_override="#38BDF8"
        )

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15, 23, 42, 0.4)",
            font=dict(color="#F8FAFC", family="Plus Jakarta Sans", size=12),
            coloraxis_showscale=False,
            height=500,
            margin=dict(t=20, b=20, l=20, r=20),
            xaxis=dict(
                showgrid=True, gridcolor="rgba(56, 189, 248, 0.1)", zeroline=True, zerolinecolor="rgba(56, 189, 248, 0.3)",
                title_font=dict(size=13, color="#F8FAFC", weight="bold"),
                tickfont=dict(size=12, color="#94A3B8")
            ),
            yaxis=dict(
                showgrid=True, gridcolor="rgba(56, 189, 248, 0.1)", zeroline=True, zerolinecolor="rgba(56, 189, 248, 0.3)",
                title_font=dict(size=13, color="#F8FAFC", weight="bold"),
                tickfont=dict(size=12, color="#94A3B8")
            )
        )
        fig.update_traces(marker=dict(opacity=0.9, line=dict(width=1, color="#38BDF8")))
        st.plotly_chart(fig, use_container_width=True)

        # Regression Impact Breakdown Module inside Visual Analysis
        st.markdown("### 📉 Regression Impact Breakdown")
        
        lin_model = LinearRegression()
        X_reg = filtered[["frpm_pct_100"]]
        y_reg = filtered["admit_rate"]
        lin_model.fit(X_reg, y_reg)
        slope = lin_model.coef_[0]
        intercept = lin_model.intercept_
        r_sq = lin_model.score(X_reg, y_reg)

        st.markdown(f"""
        <div class="analysis-box">
            <h4>📊 Statistical Linear Regression Telemetry</h4>
            <p style="color: #94A3B8; margin-bottom: 10px;">
                Calculated OLS regression mapping high school poverty concentration (<span style="color: #38BDF8;">% FRPM</span>) to institutional admission yield for <b>{selected_campus}</b> ({selected_year}):
            </p>
            <ul style="color: #F8FAFC; line-height: 1.6;">
                <li><b>Regression Slope Coefficient:</b> <code>{slope:.4f}</code>% change in acceptance rate per 1% increase in school poverty concentration.</li>
                <li><b>Baseline Intercept (0% Poverty):</b> <code>{intercept:.2f} %</code> predicted acceptance rate for completely affluent sectors.</li>
                <li><b>Model Variance Fit ($R^2$):</b> <code>{r_sq:.3f}</code> (Indicates strength of socioeconomic correlation across sector nodes).</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        st.markdown("### ⚖️ Equity & Opportunity Gap Analysis")
        st.markdown("Evaluating structural educational access barriers by analyzing disparity multipliers across institutional boundaries.")

        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.markdown(f"""
            <div class="analysis-box" style="height: 100%;">
                <h4>🔍 Opportunity Gap Ratio</h4>
                <p style="font-size: 2.2rem; font-weight: 900; color: #38BDF8; margin: 15px 0;">
                    {opp_gap_ratio}x Multiplier
                </p>
                <p style="color: #94A3B8; line-height: 1.6;">
                    Students attending low-poverty high schools (&lt;50% FRPM) experience an acceptance rate <b>{opp_gap_ratio} times higher</b> compared to peers at high-poverty institutions (≥50% FRPM) for <b>{selected_campus}</b>.
                </p>
            </div>
            """, unsafe_allow_html=True)

        with col_g2:
            st.markdown(f"""
            <div class="analysis-box" style="height: 100%;">
                <h4>🌐 Institutional Equity Index</h4>
                <p style="color: #94A3B8; line-height: 1.6; margin-top: 10px;">
                    Absolute Admission Rate Delta: <b style="color: #F8FAFC;">{abs(rate_diff):.2f}%</b>
                </p>
                <p style="color: #94A3B8; line-height: 1.6;">
                    This metric isolates systemic institutional access gaps. A higher delta reveals a widening opportunity disparity between socioeconomically disadvantaged and advantaged academic sectors.
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 🏛️ Cross-Campus Equity Benchmarks")
        
        # Calculate summary metrics across all campuses for comparison
        if "campus" in df.columns and "fall_term" in df.columns:
            comp_df = df[df["fall_term"] == selected_year].dropna(subset=["frpm_pct_100", "admits", "applicants"])
            if not comp_df.empty:
                comp_df["admit_rate"] = (comp_df["admits"] / comp_df["applicants"]) * 100
                campus_equity = []
                for camp in comp_df["campus"].unique():
                    c_data = comp_df[comp_df["campus"] == camp]
                    c_high = c_data[c_data["frpm_pct_100"] >= 50]
                    c_low = c_data[c_data["frpm_pct_100"] < 50]
                    h_r = (c_high["admits"].sum() / c_high["applicants"].sum() * 100) if c_high["applicants"].sum() > 0 else 0
                    l_r = (c_low["admits"].sum() / c_low["applicants"].sum() * 100) if c_low["applicants"].sum() > 0 else 0
                    ratio = round(l_r / h_r, 2) if h_r > 0 else 0.0
                    campus_equity.append({"Campus": camp, "Low-Pov Rate (%)": round(l_r, 2), "High-Pov Rate (%)": round(h_r, 2), "Opportunity Gap Ratio": ratio})
                
                eq_table = pd.DataFrame(campus_equity).sort_values(by="Opportunity Gap Ratio", ascending=False)
                st.dataframe(eq_table, hide_index=True, use_container_width=True)

    with tab3:
        st.markdown("### 📋 Sector Performance Indices")
        col_left, col_right = st.columns(2)

        display_cols = [col for col in ["high_school", "frpm_pct_100", "applicants", "admits", "admit_rate"] if col in filtered.columns]
        rename_map = {
            "high_school": "School Name",
            "frpm_pct_100": "Poverty Rate (%)",
            "applicants": "Applicants",
            "admits": "Admits",
            "admit_rate": "Acceptance Rate (%)"
        }

        with col_left:
            st.markdown("**🔴 High Vulnerability Sectors**")
            top_pov = filtered.sort_values(by="frpm_pct_100", ascending=False).head(10)[display_cols].copy()
            top_pov = top_pov.rename(columns=rename_map)
            st.dataframe(top_pov, hide_index=True, use_container_width=True)

        with col_right:
            st.markdown("**🟢 Low Vulnerability Sectors**")
            low_pov_table = filtered.sort_values(by="frpm_pct_100", ascending=True).head(10)[display_cols].copy()
            low_pov_table = low_pov_table.rename(columns=rename_map)
            st.dataframe(low_pov_table, hide_index=True, use_container_width=True)

    with tab4:
        st.markdown("### 📊 Distribution Topology Across Sectors")
        fig_hist = px.histogram(
            filtered,
            x="frpm_pct_100",
            nbins=25,
            labels={"frpm_pct_100": "Poverty Rate (% FRPM)", "count": "Sector Density"},
            color_discrete_sequence=["#38BDF8"]
        )
        fig_hist.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15, 23, 42, 0.4)",
            font=dict(color="#F8FAFC", family="Plus Jakarta Sans", size=12),
            height=400,
            xaxis=dict(showgrid=True, gridcolor="rgba(56, 189, 248, 0.1)", zeroline=True, zerolinecolor="rgba(56, 189, 248, 0.3)"),
            yaxis=dict(showgrid=True, gridcolor="rgba(56, 189, 248, 0.1)", zeroline=True, zerolinecolor="rgba(56, 189, 248, 0.3)")
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with tab5:
        st.markdown("### 🤖 Neural Admission Predictor Matrix")
        st.markdown("Simulate synthetic entrance vectors utilizing machine learning regression models trained on historical institutional telemetry.")

        col_pred1, col_pred2 = st.columns(2)
        
        all_schools = sorted(df["high_school"].dropna().unique()) if "high_school" in df.columns else []
        
        with col_pred1:
            st.markdown("##### 🏫 High School Origin Node")
            selected_school_pred = st.selectbox(
                "Select high school name:", 
                options=all_schools,
                index=0 if all_schools else None,
                label_visibility="collapsed"
            )
            
            st.markdown("##### 🏛️ Target Destination Node")
            target_uc_college = st.selectbox("Select UC campus you are applying to:", campuses, label_visibility="collapsed")
            
            st.markdown("##### 📚 Specialization Vector")
            input_major = st.selectbox("Select your major field of study:", ["STEM / Engineering", "Computer Science", "Biological Sciences", "Social Sciences", "Humanities / Arts", "Business / Economics"], label_visibility="collapsed")

        with col_pred2:
            st.markdown("##### 💰 Economic Capital ($)")
            input_income = st.number_input("Enter annual household income ($):", min_value=10000, max_value=500000, value=85000, step=5000, label_visibility="collapsed")
            
            school_match_row = df[df["high_school"] == selected_school_pred] if selected_school_pred else pd.DataFrame()
            
            if not school_match_row.empty and "frpm_pct_100" in school_match_row.columns:
                default_frpm = float(school_match_row["frpm_pct_100"].values[0])
            else:
                default_frpm = 35.0

            if not school_match_row.empty and "applicants" in school_match_row.columns:
                default_app_vol = int(school_match_row["applicants"].values[0])
            else:
                default_app_vol = 50

            input_frpm = default_frpm

            st.markdown("##### 👥 Cohort Volume Vector")
            input_applicants = st.number_input("Enter total applicants from your school:", min_value=1, max_value=500, value=default_app_vol, label_visibility="collapsed")

        major_weights = {
            "Computer Science": 0.6,
            "STEM / Engineering": 0.75,
            "Biological Sciences": 0.85,
            "Business / Economics": 0.85,
            "Social Sciences": 1.0,
            "Humanities / Arts": 1.1
        }
        major_multiplier = major_weights.get(input_major, 1.0)

        prediction_target_data = df[df["campus"] == target_uc_college].dropna(subset=["frpm_pct_100", "applicants", "admit_rate"])
        
        if len(prediction_target_data) > 10:
            X = prediction_target_data[["frpm_pct_100", "applicants"]]
            y = prediction_target_data["admit_rate"]
            
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X, y)
            
            base_prediction = model.predict([[input_frpm, input_applicants]])[0]
            final_prediction = base_prediction * major_multiplier
            
            st.write("")
            st.markdown("#### Simulation Result Vector:")
            st.metric(label=f"Predicted Acceptance Probability — {target_uc_college} ({input_major})", value=f"{max(0.0, min(100.0, final_prediction)):.2f}%")
            st.info(f"💡 **Neural Telemetry:** Evaluates historical vector arrays for **{target_uc_college}** given **{selected_school_pred}'s** baseline vulnerability metric ({input_frpm:.1f}%), calibrated for **{input_major}** competitiveness weightings.")
        else:
            st.warning(f"Insufficient matrix telemetry available for **{target_uc_college}** to execute simulation sequence.")
