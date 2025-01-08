# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 19:51:49 2025

@author: HP
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Parameters for the distributions
# Interarrival Times (Gamma)
interarrival_shape, interarrival_loc, interarrival_scale = 234.0233501516026, -233.22417635028626, 1.2187851104019782

# Durations (Gamma)
duration_shape, duration_loc, duration_scale = 12.584814582926688, -0.2, 0.05318623207452434

# Generate the dataset
def generate_dataset(start_date, num_days):
    data = []
    current_date = datetime.strptime(start_date, "%Y-%m-%d")

    # Start the first arrival time
    time = 8.0  # Start of the day in hours

    days_generated = 0
    interarrival_times_list = []  # List to store interarrival times for debugging

    while days_generated < num_days:
        # Skip weekends
        if current_date.weekday() in [5, 6]:  # 5: Saturday, 6: Sunday
            current_date += timedelta(days=1)
            time = 8.0  # Reset to start of the working day
            continue

        # Corrected interarrival time logic
        interarrival_time = np.random.gamma(shape=interarrival_shape, scale=interarrival_scale) + interarrival_loc
        interarrival_times_list.append(interarrival_time)  # Track interarrival times
        duration = np.random.gamma(shape=duration_shape, scale=duration_scale) + duration_loc

        # Validate interarrival times and durations
        if interarrival_time <= 0 or duration <= 0:
            continue  # Discard non-positive values

        # Update time for the next arrival
        time += interarrival_time / 60.0  # Convert interarrival times from minutes to fractional hours

        if time >= 17.0:  # End of the working day
            # Roll over to the next working day
            current_date += timedelta(days=1)
            time = 8.0 + (time - 17.0)  # Carry over remaining time past 17:00
            continue

        # Record the arrival
        data.append({
            "Date": current_date.strftime("%Y-%m-%d"),
            "Time": round(time, 2),  # Fractional hour representation
            "Duration": round(duration, 6),
            "PatientType": "Type 2"
        })

        # If a new day starts, increment the day count
        if len(data) > 1 and data[-1]["Date"] != data[-2]["Date"]:
            days_generated += 1

    interarrival_times_df = pd.DataFrame({"InterarrivalTimes": interarrival_times_list})
    interarrival_times_df.to_csv("InterarrivalTimes.csv", index=False)  # Save interarrival times for review

    return pd.DataFrame(data)

# Generate a dataset starting from the same date as in the file (Tuesday, 2023-08-01)
dataset = generate_dataset("2023-08-01", 30)

# Save the dataset to a CSV file
output_path = "C:/Users/HP/Desktop/GeneratedDataset13.csv"
dataset.to_csv(output_path, index=False)

output_path
