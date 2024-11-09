import pandas as pd

# Load the CSV file into a DataFrame
csv_file_path = "stock_data.csv"
data = pd.read_csv(csv_file_path)

# Save the DataFrame to an Excel file
excel_file_path = "stock_data.xlsx"
data.to_excel(excel_file_path, index=False)
