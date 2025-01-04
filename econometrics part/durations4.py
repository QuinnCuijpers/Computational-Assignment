# -*- coding: utf-8 -*-
"""
Created on Mon Dec 30 22:35:53 2024

@author: HP
"""

from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm, lognorm, expon, gamma, kstest

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
durations = type2_data['Duration']
mean_duration = durations.mean()
variance_duration = durations.var()
print(f"Mean of scan durations: {mean_duration:.2f}")
print(f"Variance of scan durations: {variance_duration:.2f}")

# Candidate distributions
distributions = {
    'Exponential': expon,
    'Normal': norm,
    'Gamma': gamma,
    'Log-Normal': lognorm
}

# Fit distributions and test goodness of fit
fit_results = {}
print("Fitted Parameters for Each Distribution:")
for name, dist in distributions.items():
    if name in ['Gamma', 'Log-Normal']:
        params = dist.fit(durations, floc=0)  # Force loc=0 for Gamma and Log-Normal
    else:
        params = dist.fit(durations)
    ks_stat, p_value = kstest(durations, dist.cdf, args=params)
    fit_results[name] = {'params': params, 'ks_stat': ks_stat, 'p_value': p_value}
    print(f"{name}: Parameters={params}, KS Statistic={ks_stat:.4f}, p-value={p_value:.4f}")

# Visualization of observed and fitted distributions
plt.figure(figsize=(12, 6))
plt.hist(durations, bins=30, density=True, alpha=0.6, color='blue', edgecolor='black', label='Observed Data')

x = np.linspace(min(durations), max(durations), 1000)
for name, result in fit_results.items():
    dist = distributions[name]
    params = result['params']
    pdf = dist.pdf(x, *params)
    plt.plot(x, pdf, label=f'{name} (KS={result["ks_stat"]:.2f})')

plt.title("Fitted Distributions for Durations")
plt.xlabel("Duration")
plt.ylabel("Density")
plt.legend()
plt.grid(axis='y', alpha=0.75)
plt.show()

# Monte Carlo Simulation with Multiple Runs
n_bootstrap = 1000
n_repeats = 50  # Number of Monte Carlo simulation runs
aggregated_results = {dist_name: {'mean_within_ci': [], 'var_within_ci': [], 'quantile_diffs': []}
                      for dist_name in ['Gamma', 'Log-Normal']}

bootstrap_results = {}

for dist_name in ['Gamma', 'Log-Normal']:
    dist = distributions[dist_name]
    params = fit_results[dist_name]['params']
    bootstrap_means = []
    bootstrap_variances = []

    # Bootstrap to calculate confidence intervals
    for _ in range(n_bootstrap):
        bootstrap_sample = dist.rvs(*params, size=len(durations))
        bootstrap_means.append(np.mean(bootstrap_sample))
        bootstrap_variances.append(np.var(bootstrap_sample))

    mean_ci = (np.percentile(bootstrap_means, 2.5), np.percentile(bootstrap_means, 97.5))
    variance_ci = (np.percentile(bootstrap_variances, 2.5), np.percentile(bootstrap_variances, 97.5))
    bootstrap_results[dist_name] = {'mean_ci': mean_ci, 'variance_ci': variance_ci}

    # Multiple Monte Carlo simulation runs
    for _ in range(n_repeats):
        simulated_means = []
        simulated_variances = []
        simulated_quantiles = []

        for _ in range(n_bootstrap):
            simulated_data = dist.rvs(*params, size=len(durations))
            simulated_means.append(np.mean(simulated_data))
            simulated_variances.append(np.var(simulated_data))
            simulated_quantiles.append(np.percentile(simulated_data, [25, 50, 75]))

        observed_quantiles = np.percentile(durations, [25, 50, 75])
        simulated_quantile_means = np.mean(simulated_quantiles, axis=0)
        quantile_differences = np.abs(simulated_quantile_means - observed_quantiles)

        mean_within_ci = np.mean([(mean_ci[0] <= mean <= mean_ci[1]) for mean in simulated_means])
        variance_within_ci = np.mean([(variance_ci[0] <= var <= variance_ci[1]) for var in simulated_variances])

        aggregated_results[dist_name]['mean_within_ci'].append(mean_within_ci)
        aggregated_results[dist_name]['var_within_ci'].append(variance_within_ci)
        aggregated_results[dist_name]['quantile_diffs'].append(quantile_differences)

# Summarize results for each distribution
for dist_name, results in aggregated_results.items():
    avg_mean_within_ci = np.mean(results['mean_within_ci'])
    avg_var_within_ci = np.mean(results['var_within_ci'])
    avg_quantile_diff = np.mean(results['quantile_diffs'], axis=0)
    std_quantile_diff = np.std(results['quantile_diffs'], axis=0)

    print(f"Monte Carlo Simulation Results for {dist_name} Distribution (Averaged over {n_repeats} runs):")
    print(f"Proportion of Simulated Means within Bootstrap CI: {avg_mean_within_ci:.2f}")
    print(f"Proportion of Simulated Variances within Bootstrap CI: {avg_var_within_ci:.2f}")
    print(f"Observed Quantiles (25th, 50th, 75th): {np.percentile(durations, [25, 50, 75])}")
    print(f"Simulated Quantiles Mean (25th, 50th, 75th): {avg_quantile_diff}")
    print(f"Quantile Differences (Avg): {avg_quantile_diff}")
    print(f"Quantile Differences (Std): {std_quantile_diff}\n")
