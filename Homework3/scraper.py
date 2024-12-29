import pandas as pd
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import os
import time
import ta

# Constants
BASE_URL = 'https://www.mse.mk/en/stats/symbolhistory/'
CSV_FILE = 'data.csv'

# Step 1: Extract Issuers
async def extract_issuers(session):
    async with session.get(BASE_URL + 'ALK') as response:
        soup = BeautifulSoup(await response.text(), 'html.parser')
        select_element = soup.find('select', id='Code')
        if not select_element:
            print("The company is not found")
            return []

        companies = select_element.find_all('option')
        return [option.get('value') for option in companies if
                not (option.get('value')[0] in 'EMS' or re.search(r'\d', option.get('value')))]

# Step 2: Check Last Available Date
def check_last_date(issuers):
    if os.path.exists(CSV_FILE):
        existing_data = pd.read_csv(CSV_FILE)
    else:
        existing_data = pd.DataFrame()

    today = datetime.today()
    ten_years_ago = today - timedelta(days=365 * 10)
    issuer_dates = {}

    for issuer in issuers:
        if not existing_data.empty and issuer in existing_data['company_name'].values:
            last_date_str = existing_data[existing_data['company_name'] == issuer]['date'].max()
            last_date = datetime.strptime(last_date_str, '%d/%m/%Y') + timedelta(days=1)
            issuer_dates[issuer] = last_date
        else:
            issuer_dates[issuer] = ten_years_ago

    return issuer_dates

# Step 3: Fetch Missing Data
def format_value(value):
    try:
        value = value.replace(',', '#').replace('.', ',').replace('#', '.')
        return f"{float(value):,.2f}".replace(',', ' ').replace('.', ',', 1)
    except ValueError:
        return value

async def fetch_company_data(company, start_date, end_date, session):
    stock_data = []
    url = BASE_URL + company
    async with session.get(url) as response:
        if response.status != 200:
            print(f"Failed to retrieve the page for {company}. Status code: {response.status}")
            return []

        soup = BeautifulSoup(await response.text(), 'html.parser')
        form = soup.find('form')
        if not form:
            print(f"No form found for {company}. Skipping.")
            return []

        post_url = form.get('action') if form.get('action') else url

        intervals = []
        while end_date > start_date:
            interval_start_date = max(start_date, end_date - timedelta(days=365))
            intervals.append((interval_start_date, end_date))
            end_date = interval_start_date - timedelta(days=1)

        for interval_start_date, interval_end_date in intervals:
            form_data = {
                'FromDate': interval_start_date.strftime('%m/%d/%Y'),
                'ToDate': interval_end_date.strftime('%m/%d/%Y'),
                'Code': company
            }
            try:
                async with session.post(post_url, data=form_data) as post_response:
                    if post_response.status == 200:
                        post_soup = BeautifulSoup(await post_response.text(), 'html.parser')
                        table = post_soup.find('table', {'id': 'resultsTable'})
                        if table:
                            rows = table.find_all('tr')
                            for row in rows[1:]:
                                columns = row.find_all('td')
                                if len(columns) > 0:
                                    date = datetime.strptime(columns[0].get_text(strip=True), '%m/%d/%Y').strftime(
                                        '%d/%m/%Y')
                                    stock_data.append({
                                        'company_name': company,
                                        'date': date,
                                        'last_trade_price': format_value(columns[1].get_text(strip=True)),
                                        'max_price': format_value(columns[2].get_text(strip=True)),
                                        'min_price': format_value(columns[3].get_text(strip=True)),
                                        'volume': format_value(columns[4].get_text(strip=True)),
                                        'turnover': format_value(columns[5].get_text(strip=True))
                                    })
                        else:
                            print(f"No table found for {company}. Skipping.")
                    else:
                        print(f"Failed to retrieve data for {company} ({interval_start_date} - {interval_end_date}).")
            except Exception as e:
                print(f"Error fetching data for {company}: {e}")

            print(f"Finished processing for {company} from {interval_start_date.year} to {interval_end_date.year}")

    return stock_data

# Step 4: Add Technical Indicators
    import ta

def add_technical_indicators(df):
    # Handle possible non-numeric values and ensure the columns are strings before replacing
    for column in ['last_trade_price', 'max_price', 'min_price', 'volume']:
        # Ensure the column is of string type before applying .str methods
        df[column] = df[column].astype(str).str.replace(',', '', regex=True)
        df[column] = pd.to_numeric(df[column], errors='coerce')

    # RSI for different periods (1 day, 1 week, 1 month)
    df['RSI_1D'] = ta.momentum.RSIIndicator(df['last_trade_price'], window=14).rsi()
    df['RSI_1W'] = ta.momentum.RSIIndicator(df['last_trade_price'], window=7).rsi()
    df['RSI_1M'] = ta.momentum.RSIIndicator(df['last_trade_price'], window=30).rsi()

    # MACD for different periods (1 day, 1 week, 1 month)
    macd_1D = ta.trend.MACD(df['last_trade_price'])
    df['MACD_1D'] = macd_1D.macd()
    df['MACD_signal_1D'] = macd_1D.macd_signal()

    df['EMA_fast_1W'] = df['last_trade_price'].ewm(span=7, adjust=False).mean()
    df['EMA_slow_1W'] = df['last_trade_price'].ewm(span=14, adjust=False).mean()
    df['MACD_1W'] = df['EMA_fast_1W'] - df['EMA_slow_1W']
    df['MACD_signal_1W'] = df['MACD_1W'].ewm(span=9, adjust=False).mean()

    df['EMA_fast_1M'] = df['last_trade_price'].ewm(span=12, adjust=False).mean()
    df['EMA_slow_1M'] = df['last_trade_price'].ewm(span=30, adjust=False).mean()
    df['MACD_1M'] = df['EMA_fast_1M'] - df['EMA_slow_1M']
    df['MACD_signal_1M'] = df['MACD_1M'].ewm(span=9, adjust=False).mean()

    # Stochastic Oscillator for different periods (1 day, 1 week, 1 month)
    stoch_1D = ta.momentum.StochasticOscillator(
        high=df['max_price'],
        low=df['min_price'],
        close=df['last_trade_price'],
        window=14
    )
    df['Stochastic_1D'] = stoch_1D.stoch()

    stoch_1W = ta.momentum.StochasticOscillator(
        high=df['max_price'],
        low=df['min_price'],
        close=df['last_trade_price'],
        window=7
    )
    df['Stochastic_1W'] = stoch_1W.stoch()

    stoch_1M = ta.momentum.StochasticOscillator(
        high=df['max_price'],
        low=df['min_price'],
        close=df['last_trade_price'],
        window=30
    )
    df['Stochastic_1M'] = stoch_1M.stoch()

    # Simple Moving Average (SMA) for different periods (1 day, 1 week, 1 month)
    df['SMA_1D'] = ta.trend.SMAIndicator(df['last_trade_price'], window=5).sma_indicator()
    df['SMA_1W'] = ta.trend.SMAIndicator(df['last_trade_price'], window=7).sma_indicator()
    df['SMA_1M'] = ta.trend.SMAIndicator(df['last_trade_price'], window=30).sma_indicator()

    # Bollinger Bands for different periods (1 day, 1 week, 1 month)
    bb_1D = ta.volatility.BollingerBands(df['last_trade_price'], window=5)
    df['BB_Middle_1D'] = bb_1D.bollinger_mavg()
    df['BB_Upper_1D'] = bb_1D.bollinger_hband()
    df['BB_Lower_1D'] = bb_1D.bollinger_lband()

    bb_1W = ta.volatility.BollingerBands(df['last_trade_price'], window=7)
    df['BB_Middle_1W'] = bb_1W.bollinger_mavg()
    df['BB_Upper_1W'] = bb_1W.bollinger_hband()
    df['BB_Lower_1W'] = bb_1W.bollinger_lband()

    bb_1M = ta.volatility.BollingerBands(df['last_trade_price'], window=30)
    df['BB_Middle_1M'] = bb_1M.bollinger_mavg()
    df['BB_Upper_1M'] = bb_1M.bollinger_hband()
    df['BB_Lower_1M'] = bb_1M.bollinger_lband()

    return df



# Step 5: Save to CSV
def save_to_csv(data):
    if os.path.exists(CSV_FILE):
        existing_data = pd.read_csv(CSV_FILE)
        combined_data = pd.concat([existing_data, pd.DataFrame(data)], ignore_index=True)
    else:
        combined_data = pd.DataFrame(data)

    combined_data.drop_duplicates(subset=['company_name', 'date'], inplace=True)
    combined_data.to_csv(CSV_FILE, index=False, encoding='utf-8')
    print(f"Data saved to '{CSV_FILE}'")

# Step 6: Main Function
async def main():
    start_time = time.time()

    async with aiohttp.ClientSession() as session:
        issuers = await extract_issuers(session)
        issuer_dates = check_last_date(issuers)
        all_data = []

        tasks = []
        for issuer, date in issuer_dates.items():
            task = fetch_company_data(issuer, date, datetime.today(), session)
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        for result in results:
            if result:
                all_data.extend(result)

        if all_data:
            df = pd.DataFrame(all_data)
            df = add_technical_indicators(df)
            save_to_csv(df)

    end_time = time.time()
    print(f"Data scraping and processing completed in {end_time - start_time:.2f} seconds.")

if __name__ == '__main__':
    asyncio.run(main())