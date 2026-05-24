import pandas as pd

file2 = "List of SUPPLIERS, STAFF, FACULTY.xlsx"
df = pd.read_excel(file2, sheet_name='Sheet1')
print("Unique Categories:")
print(df['Category'].unique())
