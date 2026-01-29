import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- 1. SETTINGS & THEME ---
st.set_page_config(page_title="Analyst Inventory Optimizer", layout="wide")

# Custom CSS for a "Dim/Dark Mode" Medical UI
st.markdown("""
    <style>
    /* Main Background - Deep Dark Navy */
    .stApp {
        background-color: #0e1117; 
        color: #e0e0e0;
    }
    
    /* Metric Cards - Sleek Dark Grey */
    [data-testid="stMetric"] {
        background-color: #1a1c24;
        border: 1px solid #2d2f39;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    
    /* Headers & Titles */
    h1, h2, h3 {
        color: #ffffff !important;
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar - Muted Blue-Grey */
    section[data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }

    /* Buttons */
    .stButton>button {
        background-color: #238636;
        color: white;
        border-radius: 8px;
        border: none;
    }
    
    /* Sidebar Text */
    section[data-testid="stSidebar"] .stMarkdown {
        color: #8b949e;
    }
    </style>
""", unsafe_allow_html=True)
# --- 2. LOAD DATA ---
@st.cache_data
def load_data():
    # Loading the inventory.csv you created
    df = pd.read_csv("inventory.csv")
    df['Expiry_Date'] = pd.to_datetime(df['Expiry_Date'])
    
    # Calculate "Days Remaining" logic
    df['Days_Remaining'] = (df['Current_Stock'] / df['Daily_Usage_Base']).round(1)
    
    # Calculate Status
    def get_status(days):
        if days < 7: return "CRITICAL"
        if days < 14: return "WARNING"
        return "HEALTHY"
    
    df['Status'] = df['Days_Remaining'].apply(get_status)
    return df

df = load_data()

# --- 3. HEADER SECTION ---
st.title("🔬 Analyst Inventory Optimizer")
st.subheader("Predictive Health Supply Chain Dashboard")

# --- 4. SMART METRIC CARDS ---
col1, col2, col3, col4 = st.columns(4)

critical_count = len(df[df['Status'] == "CRITICAL"])
expiring_soon = len(df[df['Expiry_Date'] < pd.Timestamp(2026, 4, 1)]) # Next 3 months

col1.metric("Total SKU Count", len(df))
col2.metric("Critical Stockouts", critical_count, delta="-2 since yesterday", delta_color="inverse")
col3.metric("Expiring Soon", expiring_soon, delta="Check Dates", delta_color="off")
col4.metric("System Health", "92%", delta="Optimal")

st.divider()

# --- 5. INTERACTIVE VISUALS ---
left_col, right_col = st.columns([2, 1])

with left_col:
    st.write("### 📊 Stock Runway (Days of Supply Left)")
    # Color mapping for the chart
    color_map = {"CRITICAL": "#ef553b", "WARNING": "#fec032", "HEALTHY": "#636efa"}
    
    fig = px.bar(
        df.sort_values("Days_Remaining"), 
        x="Days_Remaining", 
        y="Item_Name", 
        color="Status",
        orientation='h',
        color_discrete_map=color_map,
        text="Days_Remaining",
        template="plotly_white"
    )
    fig.update_layout(showlegend=False, height=500)
    st.plotly_chart(fig, use_container_width=True)

with right_col:
    st.write("### 🔔 AI Procurement Alerts")
    critical_items = df[df['Status'] == "CRITICAL"]
    for idx, row in critical_items.iterrows():
        st.error(f"**{row['Item_Name']}**: Run-out in {row['Days_Remaining']} days!")
        if st.button(f"Generate Order for {row['Item_Name']}", key=idx):
            st.info(f"Drafting Purchase Order for {row['Item_Name']}...")

# --- 6. DETAILED DATA TABLE ---
st.write("### 📋 Detailed Inventory Analysis")
def color_status(val):
    color = '#ff4b4b' if val == "CRITICAL" else ('#ffa500' if val == "WARNING" else '#28a745')
    return f'color: {color}; font-weight: bold'

st.dataframe(
    df.style.applymap(color_status, subset=['Status']),
    use_container_width=True

)
