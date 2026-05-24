import pandas as pd
from openpyxl import load_workbook

# File paths
cashbook_file = "Cashbook report (6).xlsx"
suppliers_file = "List of SUPPLIERS, STAFF, FACULTY.xlsx"

# 1. Load data
# Load Payment sheet from Cashbook
df_payment = pd.read_excel(cashbook_file, sheet_name='Payment')
# Load Supplier list
df_suppliers = pd.read_excel(suppliers_file, sheet_name='Sheet1')

# 2. Prepare columns
# We need 'Voucher no', 'Name', 'Bank', 'Amount' from Payment
# and 'Category', 'Indian/Foreign' from Suppliers
# Merging on Name/Vendor Name
df_merged = pd.merge(
    df_payment[['Voucher no', 'Name', 'Bank', 'Amount']],
    df_suppliers[['Vendor Name', 'Category', 'Indian/Foreign']],
    left_on='Name',
    right_on='Vendor Name',
    how='left'
)

# 3. Filtering
# Requested: hospital supllier, visiting faculty, visitor only
target_categories = ['hospital', 'visiting faculty', 'visitor']

# Normalize Category for filtering
df_merged['Category_Lower'] = df_merged['Category'].astype(str).str.lower().str.strip()

# Filter
# Note: "hospital supllier" might mean Hospital category.
# I'll check for "hospital", "visiting faculty", and "visitor"
filtered_df = df_merged[df_merged['Category_Lower'].isin(target_categories)].copy()

# Drop the temporary normalization column and redundant Vendor Name
filtered_df.drop(columns=['Category_Lower', 'Vendor Name'], inplace=True)

# 4. Write to a new sheet in the existing Excel file
with pd.ExcelWriter(cashbook_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    filtered_df.to_excel(writer, sheet_name='Filtered_Report', index=False)

print("Process completed successfully. New sheet 'Filtered_Report' added to Cashbook report (6).xlsx")
print(f"Total records filtered: {len(filtered_df)}")
