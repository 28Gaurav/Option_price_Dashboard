import numpy as np
from scipy.stats import norm


# intermediate variable

def inter_d1(S, K, T, r, sigma):
    return (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

def inter_d2(d1, T, sigma):
    return (d1 - sigma * np.sqrt(T))


# Option price
def option_price(S, K, T, r, sigma, option_type='call'):
    d1 = inter_d1(S, K, T, r, sigma)
    d2 = inter_d2(d1, T, sigma)
    if option_type == 'call':
        return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)


# Greeks

def delta(S, K, T, r, sigma, option_type='call'):
    d1 = inter_d1(S, K, T, r, sigma)
    if option_type == 'call':
        return norm.cdf(d1)
    else:
        return norm.cdf(d1) - 1


def gamma(S, K, T, r, sigma):
    d1 = inter_d1(S, K, T, r, sigma)
    return (norm.pdf(d1) / (S * sigma * np.sqrt(T)))  # Derivative of norm.cdf is norm.pdf


def vega(S, K, T, r, sigma, option_type="call"):
    d1 = inter_d1(S, K, T, r, sigma)
    return (S * np.sqrt(T) * norm.pdf(d1))


def theta(S, K, T, r, sigma, option_type='call'):
    d1 = inter_d1(S, K, T, r, sigma)
    d2 = inter_d2(d1, T, sigma)
    if option_type == 'call':
        return (((-S * norm.pdf(d1) * sigma) / 2 * np.sqrt(T)) - r * K * np.exp(-r * T) * norm.cdf(d2))
    else:
        return (((-S * norm.pdf(d1) * sigma) / 2 * np.sqrt(T)) + r * K * np.exp(-r * T) * norm.cdf(-d2))


def rho(S, K, T, r, sigma, option_type='call'):
    d1 = inter_d1(S, K, T, r, sigma)
    d2 = inter_d2(d1, T, sigma)
    if option_type == 'call':
        return (K * T * np.exp(-r * T) * norm.cdf(d2))
    else:
        return (-K * T * np.exp(-r * T) * norm.cdf(-d2))

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