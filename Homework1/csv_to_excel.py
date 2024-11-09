import pandas as pd

csv_file_path = "stock_data.csv"

data = pd.read_csv(csv_file_path)

excel_file_path = "stock_data.xlsx"
data.to_excel(excel_file_path, index=False)
