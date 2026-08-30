import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="UC Poverty & Admissions Dashboard", layout="wide")

st.title("📊 Socioeconomic Poverty & UC Admission Rates")
st.markdown("Analyzing UC admission outcomes across Bay Area high schools based on poverty levels (`frpm_pct`).")

@st.cache_data
def load_data():
    df = pd.read_csv("bay_area_modeling_table.csv", low_memory=False)
    return df

df = load_data()

# Sidebar controls
st.sidebar.header("Filter Settings")
selected_year = st.sidebar.selectbox("Select Fall Term", sorted(df["fall_term"].unique(), reverse=True), index=0)
poverty_threshold = st.sidebar.slider("High Poverty Threshold (% FRPM)", min_value=30, max_value=70, value=50)

# Filter dataset
filtered = df[(df["fall_term"] == selected_year) & (df["campus"] == "Universitywide")].dropna(subset=["frpm_pct", "admits", "applicants"])
filtered["admit_rate"] = (filtered["admits"] / filtered["applicants"]) * 100

# Group high vs low poverty
high_pov = filtered[filtered["frpm_pct"] >= poverty_threshold]
low_pov = filtered[filtered["frpm_pct"] < poverty_threshold]

high_rate = (high_pov["admits"].sum() / high_pov["applicants"].sum() * 100) if not high_pov.empty else 0
low_rate = (low_pov["admits"].sum() / low_pov["applicants"].sum() * 100) if not low_pov.empty else 0

# Render Key Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Selected Year", selected_year)
col2.metric(f"High Poverty Rate (≥{poverty_threshold}%)", f"{high_rate:.2f}%")
col3.metric(f"Low Poverty Rate (<{poverty_threshold}%)", f"{low_rate:.2f}%")

# Plot: Scatter Plot of Poverty Rate vs Admit Rate
st.subheader("High School Poverty Rate vs. UC Admission Rate")
fig = px.scatter(
    filtered, 
    x="frpm_pct", 
    y="admit_rate", 
    size="applicants",
    hover_name="high_school",
    labels={"frpm_pct": "Poverty Rate (% FRPM)", "admit_rate": "UC Admit Rate (%)"},
    trendline="ols"
)
st.plotly_chart(fig, use_container_width=True)
