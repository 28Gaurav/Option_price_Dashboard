import pandas as pd
from bs_model import option_price

def calculate_sensitivity(S, K, T, r, sigma, option_type):
    base = option_price(S, K, T, r, sigma, option_type)
    results = {
        'Parameter': ['Volatility (σ)', 'Interest Rate (r)', 'Spot Price (S)'],
        'Base Value': [sigma, r, S],
        '+1% Value': [sigma * 1.01, r * 1.01, S * 1.01],
        'Price Impact': [
            option_price(S, K, T, r, sigma * 1.01, option_type) - base,
            option_price(S, K, T, r * 1.01, sigma, option_type) - base,
            option_price(S * 1.01, K, T, r, sigma, option_type) - base
        ]
    }
    return pd.DataFrame(results), base

def generate_summary(df, base_price, option_type):
    summary_lines = []
    for _, row in df.iterrows():
        impact = row['Price Impact']
        percent = (impact / base_price) * 100
        direction = "raises" if percent > 0 else "lowers"
        summary_lines.append(
            f"A 1% increase in {row['Parameter']} {direction} the {option_type} price by {abs(percent):.2f}%."
        )
    return summary_lines

def perturb_sigma(S, K, T, r, sigma, option_type='call', perturbation=0.01):
    base_price = option_price(S, K, T, r, sigma, option_type)
    increased_sigma_price = option_price(S, K, T, r, sigma * (1 + perturbation), option_type)
    decreased_sigma_price = option_price(S, K, T, r, sigma * (1 - perturbation), option_type)
    return {
        'base_price': base_price,
        'sigma+1%': increased_sigma_price,
        'sigma-1%': decreased_sigma_price,
        'impact+1%': increased_sigma_price - base_price,
        'impact-1%': decreased_sigma_price - base_price
    }
