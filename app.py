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

# 2. Creamy Aesthetic & High-Contrast Typography Styling
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
