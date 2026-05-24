import pandas as pd
from openpyxl import load_workbook

# File path
cashbook_file = "Cashbook report (6).xlsx"

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
summary_detailed = df.groupby(['Category', 'Indian/Foreign']).size().unstack(fill_value=0).reset_index()

# 4. Merge summaries
final_summary = pd.merge(summary_basic, summary_detailed, on='Category', how='left')

# 5. Write the summary to a new sheet
with pd.ExcelWriter(cashbook_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    final_summary.to_excel(writer, sheet_name='Category_Summary', index=False)

print("Summary report created successfully in 'Category_Summary' sheet.")
print("\nSummary Data Preview:")
print(final_summary)
