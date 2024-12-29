# import pandas as pd
# import plotly.graph_objects as go
# from datetime import datetime
# import random
#
# # Function to generate an interactive chart for today's stock data for the given company
# def generate_today_chart_interactive(company_name, csv_file_path):
#     # Load the stock data from the CSV file
#     data = pd.read_csv(csv_file_path)
#
#     # Filter the data for the specified company
#     company_data = data[data['company_name'] == company_name]
#
#     # Clean and convert the numeric columns
#     numeric_columns = ['last_trade_price', 'max_price', 'min_price', 'volume', 'turnover']
#     for col in numeric_columns:
#         company_data[col] = company_data[col].str.replace(".", "").str.replace(",", ".").astype(float)
#
#     # Convert the date column to datetime
#     company_data['date'] = pd.to_datetime(company_data['date'], format='%d/%m/%Y')
#
#     # Filter data for today
#     today = pd.Timestamp(datetime.now().date())
#     today_data = company_data[company_data['date'] == today]
#
#     # Check if there's data for today
#     if today_data.empty:
#         print(f"No data available for {company_name} on {today.date()}")
#         return
#
#     # Prepare data for the interactive chart
#     categories = ['Last Trade', 'Max Price', 'Min Price']
#     values = [
#         today_data['last_trade_price'].values[0],
#         today_data['max_price'].values[0],
#         today_data['min_price'].values[0]
#     ]
#
#     # List of pastel colors
#     pastel_colors = [
#         "#FFB3BA", "#FFDFBA", "#FFFFBA", "#BAFFC9", "#BAE1FF", "#D7BAFF", "#FFCBA4"
#     ]
#
#     # Randomly select a pastel color
#     line_color = random.choice(pastel_colors)
#
#     # Create the interactive line chart
#     fig = go.Figure(
#         data=[go.Scatter(
#             x=categories,
#             y=values,
#             mode='lines+markers',  # Use both lines and markers
#             line=dict(color=line_color, width=2),  # Set random pastel line color
#             marker=dict(size=8),  # Set marker size
#             text=[f"{value:.2f}" for value in values],  # Add labels
#         )]
#     )
#
#     # Customize chart layout
#     fig.update_layout(
#         title=f"Stock Data for {company_name} (Today: {today.date()})",
#         xaxis_title="Category",
#         yaxis_title="Price",
#         template="plotly_white",
#         title_font_size=20,
#         title_x=0.5  # Center the title
#     )
#
#     # Show the chart
#     fig.show()
#
#
# # Example usage
# csv_file_path = "/Users/aysunsuleymanturk/Desktop/FINAL/Homework1/stock_data.csv"  # Replace with your CSV file path
# generate_today_chart_interactive("ALK", csv_file_path)


import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import plotly.io as pio


# Function to generate an interactive chart for today's stock data for the given company
def generate_two_days_ago_chart_interactive(company_name, csv_file_path):
    data = pd.read_csv(csv_file_path)

    # Filter for the specified company
    company_data = data[data['company_name'] == company_name]

    # Clean and convert numeric columns
    numeric_columns = ['last_trade_price', 'max_price', 'min_price', 'volume', 'turnover']
    for col in numeric_columns:
        company_data[col] = company_data[col].astype(str).str.replace(".", "").str.replace(",", ".").astype(float)

    # Convert date column to datetime and normalize
    company_data['date'] = pd.to_datetime(company_data['date'], format='%d/%m/%Y')
    two_days_ago = (datetime.now() - timedelta(days=2)).date()
    two_days_ago_data = company_data[company_data['date'].dt.date == two_days_ago]

    if two_days_ago_data.empty:
        return None

    # Prepare chart
    categories = ['Last Trade', 'Max Price', 'Min Price']
    values = [
        two_days_ago_data['last_trade_price'].values[0],
        two_days_ago_data['max_price'].values[0],
        two_days_ago_data['min_price'].values[0]
    ]
    pastel_colors = ["#FFB3BA", "#FFDFBA", "#FFFFBA", "#BAFFC9", "#BAE1FF"]
    line_color = random.choice(pastel_colors)
    fig = go.Figure(data=[go.Scatter(x=categories, y=values, mode='lines+markers', line=dict(color=line_color, width=3))])
    fig.update_layout(title=f"{company_name} (2 Days Ago)", xaxis_title="Category", yaxis_title="Price", template="plotly_white")

    return fig.to_html(full_html=False)
