import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Function to generate an interactive chart for monthly stock data for the given company
def generate_monthly_chart_interactive(company_name, csv_file_path):
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

    # Group the data by month and aggregate the values
    company_data['month'] = company_data['date'].dt.to_period('M')
    monthly_data = company_data.groupby('month').agg({
        'last_trade_price': 'mean',
        'max_price': 'max',
        'min_price': 'min',
        'volume': 'sum',
        'turnover': 'sum'
    }).reset_index()

    # Check if there's monthly data available
    if monthly_data.empty:
        print(f"No monthly data available for {company_name}.")
        return

    # Create the interactive line chart
    fig = go.Figure()

    # Add line for the last trade price
    fig.add_trace(go.Scatter(
        x=monthly_data['month'].astype(str),
        y=monthly_data['last_trade_price'],
        mode='lines',
        name='Last Trade Price',
        line=dict(color='#FBB18C'),  # Line color
    ))

    # Add line for max price
    fig.add_trace(go.Scatter(
        x=monthly_data['month'].astype(str),
        y=monthly_data['max_price'],
        mode='lines',
        name='Max Price',
        line=dict(color='#FF5733', dash='dot'),  # Line color and style
    ))

    # Add line for min price
    fig.add_trace(go.Scatter(
        x=monthly_data['month'].astype(str),
        y=monthly_data['min_price'],
        mode='lines',
        name='Min Price',
        line=dict(color='#C70039', dash='dash'),  # Line color and style
    ))

    # Customize chart layout
    fig.update_layout(
        title=f"Monthly Stock Data for {company_name}",
        xaxis_title="Month",
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
generate_monthly_chart_interactive(company_name, csv_file_path)
