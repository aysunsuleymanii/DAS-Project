import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Function to generate an interactive chart for 1 year's stock data for the given company
def generate_one_year_chart_interactive(company_name, csv_file_path):
    # Load the stock data from the CSV file
    data = pd.read_csv(csv_file_path)

    # Filter the data for the specified company
    company_data = data[data['company_name'] == company_name]

    # Clean and convert the numeric columns
    numeric_columns = ['last_trade_price', 'max_price', 'min_price', 'volume', 'turnover']
    for col in numeric_columns:
        company_data[col] = company_data[col].str.replace(".", "").str.replace(",", ".").astype(float)

    # Convert the date column to datetime
    company_data['date'] = pd.to_datetime(company_data['date'], format='%d/%m/%Y')

    # Filter data for the past 1 year
    one_year_ago = pd.Timestamp(datetime.now().date() - timedelta(days=365))
    one_year_data = company_data[company_data['date'] >= one_year_ago]

    # Check if there's data for the past year
    if one_year_data.empty:
        print(f"No data available for {company_name} in the last year (from {one_year_ago.date()} to today).")
        return

    # Create the interactive line chart
    fig = go.Figure()

    # Add line for the last trade price
    fig.add_trace(go.Scatter(
        x=one_year_data['date'],
        y=one_year_data['last_trade_price'],
        mode='lines',
        name='Last Trade Price',
        line=dict(color='#FBB18C'),  # Line color
    ))

    # Add line for max price
    fig.add_trace(go.Scatter(
        x=one_year_data['date'],
        y=one_year_data['max_price'],
        mode='lines',
        name='Max Price',
        line=dict(color='#FF5733', dash='dot'),  # Line color and style
    ))

    # Add line for min price
    fig.add_trace(go.Scatter(
        x=one_year_data['date'],
        y=one_year_data['min_price'],
        mode='lines',
        name='Min Price',
        line=dict(color='#C70039', dash='dash'),  # Line color and style
    ))

    # Customize chart layout
    fig.update_layout(
        title=f"Stock Data for {company_name} (Last 12 Months)",
        xaxis_title="Date",
        yaxis_title="Price",
        template="plotly_white",
        title_font_size=20,
        title_x=0.5,  # Center the title
        hovermode='x unified',  # Show the values when hovering over the chart
        legend_title="Price Type"
    )

    # Show the chart
    fig.show()


# Take user input for company name and CSV file path
company_name = input("Enter the company name: ")
csv_file_path = "/Users/aysunsuleymanturk/Desktop/FINAL/Homework1/stock_data.csv"

# Call the function with user inputs
generate_one_year_chart_interactive(company_name, csv_file_path)

