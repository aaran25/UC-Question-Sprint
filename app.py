import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="UC Poverty & Admissions Dashboard", layout="wide")

st.title("📊 Socioeconomic Poverty & UC Admission Rates")
st.markdown("Analyzing UC admission outcomes across Bay Area high schools based on poverty levels (`frpm_pct`).")

@st.cache_data
def load_data():
    df = pd.read_csv("bay_area_modeling_table.csv", low_memory=False)
    # Ensure frpm_pct is on a 0-100 scale for intuitive slider comparison
    if df["frpm_pct"].max() <= 1.0:
        df["frpm_pct_100"] = df["frpm_pct"] * 100
    else:
        df["frpm_pct_100"] = df["frpm_pct"]
    return df

df = load_data()

# Sidebar controls
st.sidebar.header("Filter Settings")
selected_year = st.sidebar.selectbox("Select Fall Term", sorted(df["fall_term"].unique(), reverse=True), index=0)
poverty_threshold = st.sidebar.slider("High Poverty Threshold (% FRPM)", min_value=10, max_value=90, value=50)

# Filter dataset
filtered = df[(df["fall_term"] == selected_year) & (df["campus"] == "Universitywide")].dropna(subset=["frpm_pct_100", "admits", "applicants"])
filtered["admit_rate"] = (filtered["admits"] / filtered["applicants"]) * 100

# Group high vs low poverty
high_pov = filtered[filtered["frpm_pct_100"] >= poverty_threshold]
low_pov = filtered[filtered["frpm_pct_100"] < poverty_threshold]

high_rate = (high_pov["admits"].sum() / high_pov["applicants"].sum() * 100) if not high_pov.empty else 0
low_rate = (low_pov["admits"].sum() / low_pov["applicants"].sum() * 100) if not low_pov.empty else 0

# Metric Display Cards
m1, m2, m3 = st.columns(3)
m1.metric("Selected Term", selected_year)
m2.metric(f"High Poverty Admit Rate (≥{poverty_threshold}%)", f"{high_rate:.2f}%")
m3.metric(f"Low Poverty Admit Rate (<{poverty_threshold}%)", f"{low_rate:.2f}%", delta=f"{low_rate - high_rate:+.2f}% vs High Pov", delta_color="normal")

st.markdown("---")

# Styled Scatter Plot
fig = px.scatter(
    filtered,
    x="frpm_pct_100",
    y="admit_rate",
    size="applicants",
    color="frpm_pct_100",
    color_continuous_scale="Viridis",
    hover_name="school_name" if "school_name" in filtered.columns else None,
    hover_data=["applicants", "admits"],
    labels={
        "frpm_pct_100": "Poverty Rate (% FRPM)",
        "admit_rate": "UC Admit Rate (%)",
        "applicants": "Total Applicants"
    },
    title=f"High School Poverty Rate vs. UC Admission Rate ({selected_year})",
    trendline="ols"
)

fig.update_layout(template="plotly_dark", height=600)
st.plotly_chart(fig, use_container_width=True)
