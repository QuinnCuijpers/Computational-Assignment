import pandas as pd

df1 = pd.read_csv("econometrics part/simulated_type1_patients_formatted.csv")
df2 = pd.read_csv("econometrics part/GeneratedDatasetType 2.csv")

df = pd.concat([df1, df2], ignore_index=True)
print(df.head())

sorted_df = df.sort_values(by=["Date", "Time"], inplace=False)
print(sorted_df.head())

sorted_df.to_csv("generated_data.csv", index=False)
