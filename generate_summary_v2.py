import pandas as pd

# File path
cashbook_file = "Cashbook report (6).xlsx"
summary_file = "Category_Summary.xlsx"

# 1. Load the filtered data
df = pd.read_excel(cashbook_file, sheet_name='Filtered_Report')

# 2. Calculate Summary
# Group by Category to get:
# - Total count (Number of vouchers)
# - Total Amount
summary_basic = df.groupby('Category').agg(
    Total_Count=('Voucher no', 'count'),
    Total_Amount=('Amount', 'sum')
).reset_index()

# 3. Calculate Indian/Foreign counts per category
# Assuming 'Indian/Foreign' is the column name from previous merge
# We need to handle potential missing columns if merge failed for some rows
if 'Indian/Foreign' in df.columns:
    summary_detailed = df.groupby(['Category', 'Indian/Foreign']).size().unstack(fill_value=0).reset_index()
    final_summary = pd.merge(summary_basic, summary_detailed, on='Category', how='left')
else:
    final_summary = summary_basic

# 4. Write the summary to a NEW file to avoid permission issues
final_summary.to_excel(summary_file, index=False)

print("Summary report created successfully in 'Category_Summary.xlsx'.")
print("\nSummary Data Preview:")
print(final_summary)
