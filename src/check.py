
import pandas as pd

df = pd.read_csv("data/raw/complaints.csv")

print("Total Records:", len(df))
print("Total Columns:", len(df.columns))

print("\nColumn Names:")
print(df.columns.tolist())

print("\nFirst 5 Records:")
print(df.head())

print("\nMissing Values:")
print(df.isnull().sum())
