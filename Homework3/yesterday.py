import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# Function to generate an interactive chart for 2 days ago's stock data for the given company
def generate_two_days_ago_chart_interactive(company_name, csv_file_path):
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

    # Filter data for 2 days ago
    two_days_ago = pd.Timestamp(datetime.now().date() - timedelta(days=2))
    two_days_ago_data = company_data[company_data['date'] == two_days_ago]

    # Check if there's data for 2 days ago
    if two_days_ago_data.empty:
        print(f"No data available for {company_name} on {two_days_ago.date()}")
        return

    # Prepare data for the interactive line chart
    categories = ['Last Trade', 'Max Price', 'Min Price']
    values = [
        two_days_ago_data['last_trade_price'].values[0],
        two_days_ago_data['max_price'].values[0],
        two_days_ago_data['min_price'].values[0]
    ]

    # List of pastel colors for the line chart
    pastel_colors = [
        "#FF7F7F", "#FFB87D", "#FFFF66", "#80FF80", "#7FBFFF", "#B49BFF", "#FF9E6B",  # Original shades
        "#FF6F61", "#FFB766", "#FFDD66", "#66FF66", "#66B3FF", "#9A66FF", "#FF7F4C",  # New shades
        "#FF6655", "#FFB34D", "#FFFF33", "#66FF44", "#33BFFF", "#9966FF", "#FF8C5C"  # Additional shades
    ]

    # Randomly select a pastel color
    line_color = random.choice(pastel_colors)

    # Create the interactive line chart
    fig = go.Figure(
        data=[go.Scatter(
            x=categories,
            y=values,
            mode='lines+markers',
            line=dict(color=line_color, width=3),
            marker=dict(size=8),
            text=[f"{value:.2f}" for value in values],  # Add labels for the points
            textposition='top center'  # Position labels above the markers
        )]
    )

    # Customize chart layout
    fig.update_layout(
        title=f"Stock Data for {company_name} (2 Days Ago: {two_days_ago.date()})",
        xaxis_title="Category",
        yaxis_title="Price",
        template="plotly_white",
        title_font_size=20,
        title_x=0.5,  # Center the title
        showlegend=False
    )

    # Show the chart
    fig.show()


# Example usage
csv_file_path = "/Users/aysunsuleymanturk/Desktop/FINAL/Homework1/stock_data.csv"  # Replace with your CSV file path
generate_two_days_ago_chart_interactive("TTK", csv_file_path)
