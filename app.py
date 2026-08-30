import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="UC Admissions Dashboard", layout="wide")

st.title("🎓 UC Admissions Explorer (2021–2025)")
st.markdown("Analyzing applicant outcomes across California public high schools.")

@st.cache_data
def load_data():
    df = pd.read_csv("bay_area_modeling_table.csv", low_memory=False)
    return df

df = load_data()

# Sidebar Filters
st.sidebar.header("Filter Options")
selected_campuses = st.sidebar.multiselect(
    "Select Campuses", 
    options=df["campus"].dropna().unique(),
    default=["UCB", "UCLA"] if "UCB" in df["campus"].values else [df["campus"].iloc[0]]
)

year_range = st.sidebar.slider(
    "Select Year Range",
    min_value=int(df["fall_term"].min()),
    max_value=int(df["fall_term"].max()),
    value=(2021, 2025)
)

# Apply Filters
filtered_df = df[
    (df["campus"].isin(selected_campuses)) &
    (df["fall_term"].between(year_range[0], year_range[1]))
]

# Key Performance Indicators (KPIs)
col1, col2, col3 = st.columns(3)
total_apps = filtered_df["applicants"].sum()
total_admits = filtered_df["admits"].sum()
overall_rate = (total_admits / total_apps * 100) if total_apps > 0 else 0

col1.metric("Total Applicants", f"{total_apps:,.0f}")
col2.metric("Total Admits", f"{total_admits:,.0f}")
col3.metric("Overall Admit Rate", f"{overall_rate:.2f}%")

# Plot: Trend over time
st.subheader("Admit Rate Trends Over Time")
trend_df = filtered_df.groupby(["fall_term", "campus"])[["admits", "applicants"]].sum().reset_index()
trend_df["admit_rate"] = (trend_df["admits"] / trend_df["applicants"]) * 100

fig = px.line(
    trend_df, 
    x="fall_term", 
    y="admit_rate", 
    color="campus",
    markers=True,
    labels={"fall_term": "Fall Term", "admit_rate": "Admit Rate (%)"}
)
st.plotly_chart(fig, use_container_width=True)
