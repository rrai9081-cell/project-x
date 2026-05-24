import pandas as pd

file1 = "Cashbook report (6).xlsx"
file2 = "List of SUPPLIERS, STAFF, FACULTY.xlsx"

print(f"File: {file1}")
xls1 = pd.ExcelFile(file1)
print(f"Sheets: {xls1.sheet_names}")
for sheet in xls1.sheet_names:
    df = pd.read_excel(file1, sheet_name=sheet, nrows=5)
    print(f"Sheet: {sheet}, Columns: {df.columns.tolist()}")
    
print(f"\nFile: {file2}")
xls2 = pd.ExcelFile(file2)
print(f"Sheets: {xls2.sheet_names}")
for sheet in xls2.sheet_names:
    df = pd.read_excel(file2, sheet_name=sheet, nrows=5)
    print(f"Sheet: {sheet}, Columns: {df.columns.tolist()}")
