import pandas as pd
df = pd.read_csv("Sample - Superstore.csv", encoding="windows-1252")

print(df.groupby("Discount")["Profit"].mean().round(1))      # Q1
print(df.groupby("Category")["Profit"].sum().round(0))       # Q2
print(df.groupby("Region")["Profit"].sum().round(0))         # Q2