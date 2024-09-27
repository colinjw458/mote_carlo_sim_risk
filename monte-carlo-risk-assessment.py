import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime, timedelta

def fetch_stock_data(ticker, start_date, end_date):
    stock = yf.Ticker(ticker)
    hist = stock.history(start=start_date, end=end_date)
    returns = hist['Close'].pct_change().dropna()
    return returns, stock.info['longName']

def monte_carlo_simulation(returns, num_simulations, initial_investment, time_horizon):
    mean_return = returns.mean()
    volatility = returns.std()
    
    daily_returns = np.random.normal(mean_return, volatility, (num_simulations, time_horizon))
    cumulative_returns = np.cumprod(1 + daily_returns, axis=1)
    final_values = initial_investment * cumulative_returns[:, -1]
    
    return final_values, cumulative_returns

def calculate_var(final_values, confidence_level):
    return np.percentile(final_values, 100 - confidence_level)

def calculate_cvar(final_values, confidence_level):
    var = calculate_var(final_values, confidence_level)
    return final_values[final_values <= var].mean()

# Parameters
ticker = "AAPL"  # Apple Inc. stock
start_date = (datetime.now() - timedelta(days=365*5)).strftime('%Y-%m-%d')
end_date = datetime.now().strftime('%Y-%m-%d')
num_simulations = 10000
initial_investment = 100000
time_horizon = 252  # roughly one trading year
confidence_level = 95

# Fetch historical data
returns, company_name = fetch_stock_data(ticker, start_date, end_date)

# Run simulation
final_values, cumulative_returns = monte_carlo_simulation(returns, num_simulations, initial_investment, time_horizon)

# Calculate risk metrics
var_95 = calculate_var(final_values, confidence_level)
cvar_95 = calculate_cvar(final_values, confidence_level)

# Print results
print(f"Stock: {company_name} ({ticker})")
print(f"Value at Risk (95% confidence): ${var_95:.2f}")
print(f"Conditional Value at Risk (95% confidence): ${cvar_95:.2f}")

# Plotting in separate windows
plt.figure(figsize=(12, 6))
plt.plot(cumulative_returns[:100].T * initial_investment)
plt.title(f'Monte Carlo Simulation: {num_simulations} Runs\n{company_name} ({ticker})')
plt.xlabel('Trading Days')
plt.ylabel('Portfolio Value ($)')
plt.tight_layout()

plt.figure(figsize=(12, 6))
plt.hist(final_values, bins=50, edgecolor='black')
plt.title(f'Distribution of Portfolio Values After 1 Year\n{company_name} ({ticker})')
plt.xlabel('Portfolio Value ($)')
plt.ylabel('Frequency')
plt.axvline(var_95, color='r', linestyle='dashed', linewidth=2, label=f'VaR {confidence_level}%')
plt.axvline(cvar_95, color='g', linestyle='dashed', linewidth=2, label=f'CVaR {confidence_level}%')
plt.legend()
plt.tight_layout()

plt.figure(figsize=(12, 6))
returns.hist(bins=50, edgecolor='black')
plt.title(f'Historical Daily Returns\n{company_name} ({ticker})')
plt.xlabel('Daily Return')
plt.ylabel('Frequency')
plt.tight_layout()

plt.show()