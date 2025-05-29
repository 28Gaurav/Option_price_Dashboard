import streamlit as st
import numpy as np
import plotly.express as px
import pandas as pd
from bs_model import *
from utils import calculate_sensitivity_detailed, generate_summary_line, perturb_sigma

st.set_page_config(page_title="Options Pricing Dashboard", layout="wide")
st.title("Options Pricing Sensitivity Dashboard")

# Sidebar
with st.sidebar:
    st.header("Input Parameters")
    S = st.slider("Spot Price (S)", 1.0, 500.0, 100.0)
    K = st.slider("Strike Price (K)", 1.0, 500.0, 100.0)
    T = st.slider("Time to Maturity (T, in years)", 0.1, 5.0, 1.0, 0.1)
    sigma = st.slider("Volatility (σ)", 0.01, 2.0, 0.2, 0.01)
    r = st.slider("Risk-free Rate (r)", 0.0, 0.2, 0.05, 0.005)
    option_type = st.radio("Option Type", ["call", "put"], horizontal=True)

#Option Price Curve
def plot_price_curve(S, K, T, r, sigma, option_type):
    S_range = np.linspace(max(1, S * 0.5), min(S * 2, 1000), 100)
    prices = [option_price(s, K, T, r, sigma, option_type) for s in S_range]
    fig = px.line(x=S_range, y=prices,
                  title="Option Price vs. Underlying Price",
                  labels={"x": "Underlying Price (S)", "y": "Option Price"})
    fig.add_vline(x=K, line_dash="dash", line_color="red")
    st.plotly_chart(fig, use_container_width=True)

# Multiline plot for Greeks vs Spot price or underlying price
def plot_greeks_multiline(S, K, T, r, sigma, option_type):
    S_range = np.linspace(S * 0.5, S * 1.5, 100)
    greek_data = {
        "S": S_range,
        "Delta": [delta(s, K, T, r, sigma, option_type) for s in S_range],
        "Gamma": [gamma(s, K, T, r, sigma) for s in S_range],
        "Vega": [vega(s, K, T, r, sigma) for s in S_range],
        "Theta": [theta(s, K, T, r, sigma, option_type) for s in S_range],
        "Rho": [rho(s, K, T, r, sigma, option_type) for s in S_range],
    }
    df = pd.DataFrame(greek_data)
    df_long = df.melt(id_vars="S", var_name="Greek", value_name="Value")
    fig = px.line(df_long, x="S", y="Value", color="Greek", title="Greeks vs Underlying Price")
    st.plotly_chart(fig, use_container_width=True)

# Layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("Price Analysis")
    plot_price_curve(S, K, T, r, sigma, option_type)
    current_price = option_price(S, K, T, r, sigma, option_type)
    st.metric("Current Option Price", f"${current_price:.2f}")

with col2:
    st.subheader("Greeks Analysis")
    plot_greeks_multiline(S, K, T, r, sigma, option_type)

#Sensitivity Analysis
st.subheader("Parameter Sensitivity Panel")
sensitivity_tables = calculate_sensitivity_detailed(S, K, T, r, sigma, option_type)

for param, df in sensitivity_tables.items():
    st.markdown(f"### {param}")
    st.dataframe(df.style.format({
        "Base": "{:.4f}",
        "+1% Value": "{:.4f}",
        "Impact": "{:+.4f}"
    }), use_container_width=True)


#Stability Check for Sigma
st.subheader("Stability Check: Volatility (σ) Perturbation")

st.caption("Analyzing effect of ±1% change in volatility")

perturb_result = perturb_sigma(S, K, T, r, sigma, option_type)
st.write(f"- Base Price: **${perturb_result['base_price']:.4f}**")
st.write(f"- σ +1% → Price: **${perturb_result['sigma+1%']:.4f}** (Impact: {perturb_result['impact+1%']:+.4f})")
st.write(f"- σ -1% → Price: **${perturb_result['sigma-1%']:.4f}** (Impact: {perturb_result['impact-1%']:+.4f})")

#Summary
st.subheader("Summary")

for param, df in sensitivity_tables.items():
    price_row = df[df["Metric"] == "Price"].iloc[0]
    summary = generate_summary_line(param, price_row["Impact"], price_row["Base"], option_type)
    st.write(f"- {summary}")
