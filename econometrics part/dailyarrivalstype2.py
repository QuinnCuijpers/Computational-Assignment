# -*- coding: utf-8 -*-
"""
Created on Mon Dec 30 23:09:02 2024

@author: HP
"""

from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import poisson, norm, gamma, kstest, expon, lognorm

# Load the data
file_path = "C:/Users/HP/Desktop/ScanRecords.xlsx"
data = pd.ExcelFile(file_path)
scan_data = data.parse('ScanRecords')

# Ensure proper data types
scan_data['Date'] = pd.to_datetime(scan_data['Date'], format='%Y-%m-%d')
scan_data['Time'] = pd.to_numeric(scan_data['Time'], errors='coerce')
scan_data['PatientType'] = scan_data['PatientType'].astype(str)

# Filter for Type 2 patients
type2_data = scan_data[scan_data['PatientType'] == 'Type 2']

# Count arrivals per day
daily_arrivals = type2_data.groupby('Date').size()

# Print mean and variance of daily arrivals
mean_arrivals = daily_arrivals.mean()
variance_arrivals = daily_arrivals.var()
print(f"Mean of daily arrivals: {mean_arrivals:.2f}")
print(f"Variance of daily arrivals: {variance_arrivals:.2f}")

# Distribution fitting
print("Fitting distributions to Type 2 daily arrivals:")

# Candidate distributions
distributions = {
    'Poisson': poisson,
    'Normal': norm,
    'Gamma': gamma,
    'Log-Normal': lognorm,
    'Exponential': expon
}

fit_results = {}

for name, dist in distributions.items():
    if name == 'Poisson':
        # Poisson only has one parameter (lambda), mean of the data
        params = (daily_arrivals.mean(),)
        ks_stat, p_value = kstest(daily_arrivals, dist.cdf, args=params)
    else:
        params = dist.fit(daily_arrivals)
        ks_stat, p_value = kstest(daily_arrivals, dist.cdf, args=params)

    fit_results[name] = {'params': params, 'ks_stat': ks_stat, 'p_value': p_value}
    print(f"{name}: Parameters={params}, KS Statistic={ks_stat:.4f}, p-value={p_value:.4f}")

# Plot the observed distribution and fitted PDFs
plt.figure(figsize=(12, 6))
plt.hist(daily_arrivals, bins=range(daily_arrivals.min(), daily_arrivals.max() + 2),
         density=True, alpha=0.6, color='blue', edgecolor='black', label='Observed Data')

x = np.linspace(daily_arrivals.min(), daily_arrivals.max(), 1000)
for name, result in fit_results.items():
    dist = distributions[name]
    params = result['params']
    if name == 'Poisson':
        pmf = dist.pmf(np.floor(x), *params)
        plt.plot(x, pmf, label=f'{name} (KS={result["ks_stat"]:.2f})')
    else:
        pdf = dist.pdf(x, *params)
        plt.plot(x, pdf, label=f'{name} (KS={result["ks_stat"]:.2f})')

plt.title("Fitted Distributions for Type 2 Patient Daily Arrivals")
plt.xlabel("Number of Arrivals")
plt.ylabel("Density")
plt.legend()
plt.grid(axis='y', alpha=0.75)
plt.show()

# Visualizing the time series of daily arrivals
plt.figure(figsize=(14, 6))
plt.plot(daily_arrivals.index, daily_arrivals.values, marker='o', linestyle='-', color='blue')
plt.title("Time Series of Type 2 Patient Daily Arrivals")
plt.xlabel("Date")
plt.ylabel("Number of Arrivals")
plt.grid(axis='y', alpha=0.75)
plt.show()
