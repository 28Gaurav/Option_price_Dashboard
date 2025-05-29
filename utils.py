import pandas as pd
from bs_model import option_price, delta, gamma, vega, theta, rho

def calculate_sensitivity_detailed(S, K, T, r, sigma, option_type):
    base_price = option_price(S, K, T, r, sigma, option_type)
    base_greeks = {
        "Delta": delta(S, K, T, r, sigma, option_type),
        "Gamma": gamma(S, K, T, r, sigma),
        "Vega": vega(S, K, T, r, sigma),
        "Theta": theta(S, K, T, r, sigma, option_type),
        "Rho": rho(S, K, T, r, sigma, option_type),
    }

    param_sets = [
        ("Volatility (σ)", sigma, sigma * 1.01, S, K, T, r, sigma * 1.01),
        ("Interest Rate (r)", r, r * 1.01, S, K, T, r * 1.01, sigma),
        ("Spot Price (S)", S, S * 1.01, S * 1.01, K, T, r, sigma),
    ]

    tables = {}

    for param, base_val, perturbed_val, S_p, K_p, T_p, r_p, sigma_p in param_sets:
        price_perturbed = option_price(S_p, K_p, T_p, r_p, sigma_p, option_type)
        greek_perturbed = {
            "Delta": delta(S_p, K_p, T_p, r_p, sigma_p, option_type),
            "Gamma": gamma(S_p, K_p, T_p, r_p, sigma_p),
            "Vega": vega(S_p, K_p, T_p, r_p, sigma_p),
            "Theta": theta(S_p, K_p, T_p, r_p, sigma_p, option_type),
            "Rho": rho(S_p, K_p, T_p, r_p, sigma_p, option_type),
        }

        data = {
            "Metric": ["Price"] + list(base_greeks.keys()),
            "Base": [base_price] + list(base_greeks.values()),
            "+1% Value": [price_perturbed] + list(greek_perturbed.values()),
            "Impact": [price_perturbed - base_price] +
                      [greek_perturbed[k] - base_greeks[k] for k in base_greeks]
        }

        tables[param] = pd.DataFrame(data)

    return tables

def generate_summary_line(parameter, impact, base_price, option_type):
    percent = (impact / base_price) * 100 if base_price != 0 else 0
    direction = "raises" if impact > 0 else "lowers"
    return f"A 1% increase in {parameter} {direction} the {option_type} price by {abs(percent):.2f}%."

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
