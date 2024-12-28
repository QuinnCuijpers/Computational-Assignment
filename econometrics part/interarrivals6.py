# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 18:49:36 2024

@author: HP
"""

from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm, lognorm, expon, kstest, gamma, poisson

# Load the data
file_path = "C:/Users/HP/Desktop/ScanRecords.xlsx"
data = pd.ExcelFile(file_path)
scan_data = data.parse('ScanRecords')

# Data Overview
print(scan_data.head())

# Ensure proper data types
scan_data['Date'] = pd.to_datetime(scan_data['Date'], format='%Y-%m-%d')
scan_data['Time'] = pd.to_numeric(scan_data['Time'], errors='coerce')
scan_data['Duration'] = pd.to_numeric(scan_data['Duration'], errors='coerce')
scan_data['PatientType'] = scan_data['PatientType'].astype(str)

# Filter for Type 2 patients
type2_data = scan_data[scan_data['PatientType'] == 'Type 2']

# Create Datetime for inter-arrival time calculation
type2_data['Datetime'] = type2_data['Date'] + pd.to_timedelta(type2_data['Time'], unit='h')
type2_data = type2_data.sort_values(by='Datetime')

# Function to calculate adjusted inter-arrival times
def calculate_interarrival_time(current, previous):
    if pd.isnull(previous):
        return None

    total_minutes = 0
    while previous.date() < current.date():
        if previous.hour < 17:
            total_minutes += (17 - max(8, previous.hour)) * 60 - previous.minute
        previous += timedelta(days=1)
        previous = previous.replace(hour=8, minute=0)
        if previous.weekday() >= 5:
            previous += timedelta(days=(7 - previous.weekday()))

    if current.hour >= 8 and current.hour < 17:
        total_minutes += (current.hour - max(8, previous.hour)) * 60 + (current.minute - previous.minute)

    return total_minutes

# Exclude weekends and non-working hours
type2_data = type2_data[
    (type2_data['Datetime'].dt.weekday < 5) &
    (type2_data['Datetime'].dt.hour >= 8) &
    (type2_data['Datetime'].dt.hour < 17)
]

type2_data['PreviousDatetime'] = type2_data['Datetime'].shift(1)
type2_data['AdjustedInterArrivalTimeMinutes'] = type2_data.apply(
    lambda row: calculate_interarrival_time(row['Datetime'], row['PreviousDatetime']),
    axis=1
)

type2_data = type2_data.dropna(subset=['AdjustedInterArrivalTimeMinutes'])

# Find the largest adjusted inter-arrival time
max_adjusted_time = type2_data['AdjustedInterArrivalTimeMinutes'].max()
max_adjusted_row = type2_data[type2_data['AdjustedInterArrivalTimeMinutes'] == max_adjusted_time]
print(f"Largest Adjusted Inter-Arrival Time: {max_adjusted_time:.2f} minutes")
print(max_adjusted_row)

# Visualize the distribution
plt.figure(figsize=(10, 6))
plt.hist(type2_data['AdjustedInterArrivalTimeMinutes'], bins=30, alpha=0.7, color='blue', edgecolor='black')
plt.title("Distribution of Adjusted Inter-Arrival Times")
plt.xlabel("Inter-Arrival Time (minutes)")
plt.ylabel("Frequency")
plt.grid(axis='y', alpha=0.75)
plt.show()

# Candidate distributions
interarrival_times = type2_data['AdjustedInterArrivalTimeMinutes']
distributions = {
    'Exponential': expon,
    'Normal': norm,
    'Gamma': gamma,
    'Log-Normal': lognorm
}

# Fit distributions and test goodness of fit
fit_results = {}
print("Goodness-of-Fit Results with Fitted Parameters:")
for name, dist in distributions.items():
    # Fit the distribution
    params = dist.fit(interarrival_times)
    
    # Perform KS test
    ks_stat, ks_pvalue = kstest(interarrival_times, dist.cdf, args=params)
    
    # Store results
    fit_results[name] = {'params': params, 'ks_stat': ks_stat, 'ks_pvalue': ks_pvalue}
    
    # Print fitted parameters
    print(f"{name}: Parameters (shape, loc, scale)={params}")
    print(f"KS Statistic={ks_stat:.4f}, p-value={ks_pvalue:.4f}\n")

# Add Poisson fitting
poisson_lambda = np.mean(interarrival_times)
poisson_cdf = lambda x: poisson.cdf(x, mu=poisson_lambda)
ks_stat, ks_pvalue = kstest(interarrival_times, poisson_cdf)
fit_results['Poisson'] = {'params': (poisson_lambda,), 'ks_stat': ks_stat, 'ks_pvalue': ks_pvalue}

# Print Poisson results
print(f"Poisson: Parameters (lambda)={poisson_lambda:.2f}")
print(f"KS Statistic={ks_stat:.4f}, p-value={ks_pvalue:.4f}\n")

# Plot histogram and fitted PDFs
plt.figure(figsize=(12, 6))
plt.hist(interarrival_times, bins=30, density=True, alpha=0.6, color='blue', edgecolor='black', label='Observed')

x = np.linspace(interarrival_times.min(), interarrival_times.max(), 1000)
for name, result in fit_results.items():
    if name == 'Poisson':
        pdf = poisson.pmf(np.floor(x), mu=result['params'][0])
    else:
        dist = distributions[name]
        params = result['params']
        pdf = dist.pdf(x, *params)
    plt.plot(x, pdf, label=f'{name} (KS={result["ks_stat"]:.2f})')

plt.title("Fitted Distributions for Inter-Arrival Times")
plt.xlabel("Inter-Arrival Time (minutes)")
plt.ylabel("Density")
plt.legend()
plt.grid(axis='y', alpha=0.75)
plt.show()

# Parametric Bootstrap for Gamma
gamma_params = gamma.fit(interarrival_times)
shape, loc, scale = gamma_params

n_bootstrap = 1000
bootstrap_means = []
bootstrap_variances = []

for _ in range(n_bootstrap):
    bootstrap_sample = gamma.rvs(shape, loc=loc, scale=scale, size=len(interarrival_times))
    bootstrap_sample = bootstrap_sample[bootstrap_sample >= 0]  # Remove negative values
    bootstrap_means.append(np.mean(bootstrap_sample))
    bootstrap_variances.append(np.var(bootstrap_sample))

bootstrap_mean_ci = (np.percentile(bootstrap_means, 2.5), np.percentile(bootstrap_means, 97.5))
bootstrap_variance_ci = (np.percentile(bootstrap_variances, 2.5), np.percentile(bootstrap_variances, 97.5))

print("Bootstrap Results for Gamma Distribution:")
print(f"Bootstrap Mean Confidence Interval (95%): {bootstrap_mean_ci[0]:.2f}, {bootstrap_mean_ci[1]:.2f}")
print(f"Bootstrap Variance Confidence Interval (95%): {bootstrap_variance_ci[0]:.2f}, {bootstrap_variance_ci[1]:.2f}\n")

# Monte Carlo Simulation
n_simulations = 1000
simulated_means = []
simulated_variances = []
simulated_quantiles = []

for _ in range(n_simulations):
    simulated_data = gamma.rvs(shape, loc=loc, scale=scale, size=len(interarrival_times))
    simulated_data = simulated_data[simulated_data >= 0]  # Remove negative values
    simulated_means.append(np.mean(simulated_data))
    simulated_variances.append(np.var(simulated_data))
    simulated_quantiles.append(np.percentile(simulated_data, [25, 50, 75]))

# Quantile Comparison
observed_quantiles = np.percentile(interarrival_times, [25, 50, 75])
simulated_quantiles_avg = np.mean(simulated_quantiles, axis=0)

print(f"Observed Quantiles (25th, 50th, 75th): {observed_quantiles}")
print(f"Simulated Quantiles (25th, 50th, 75th): {simulated_quantiles_avg}")

# Visualization
plt.figure(figsize=(14, 8))

plt.subplot(2, 2, 1)
plt.hist(bootstrap_means, bins=30, alpha=0.7, color='blue', edgecolor='black')
plt.axvline(bootstrap_mean_ci[0], color='red', linestyle='--', label='Lower CI Bound')
plt.axvline(bootstrap_mean_ci[1], color='green', linestyle='--', label='Upper CI Bound')
plt.title("Bootstrap Means")
plt.xlabel("Mean")
plt.ylabel("Frequency")
plt.legend()

plt.subplot(2, 2, 2)
plt.hist(bootstrap_variances, bins=30, alpha=0.7, color='orange', edgecolor='black')
plt.axvline(bootstrap_variance_ci[0], color='red', linestyle='--', label='Lower CI Bound')
plt.axvline(bootstrap_variance_ci[1], color='green', linestyle='--', label='Upper CI Bound')
plt.title("Bootstrap Variances")
plt.xlabel("Variance")
plt.ylabel("Frequency")
plt.legend()

plt.subplot(2, 2, 3)
plt.hist(simulated_means, bins=30, alpha=0.7, color='purple', edgecolor='black')
plt.axvline(bootstrap_mean_ci[0], color='red', linestyle='--', label='Lower CI Bound')
plt.axvline(bootstrap_mean_ci[1], color='green', linestyle='--', label='Upper CI Bound')
plt.title("Simulated Means")
plt.xlabel("Mean")
plt.ylabel("Frequency")
plt.legend()

plt.subplot(2, 2, 4)
plt.hist(simulated_variances, bins=30, alpha=0.7, color='teal', edgecolor='black')
plt.axvline(bootstrap_variance_ci[0], color='red', linestyle='--', label='Lower CI Bound')
plt.axvline(bootstrap_variance_ci[1], color='green', linestyle='--', label='Upper CI Bound')
plt.title("Simulated Variances")
plt.xlabel("Variance")
plt.ylabel("Frequency")
plt.legend()

plt.tight_layout()
plt.show()
