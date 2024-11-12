import pandas as pd
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import os
import time

BASE_URL = 'https://www.mse.mk/en/stats/symbolhistory/'
CSV_FILE = 'stock_data.csv'


# Filter 1: Extract Issuers
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


# Filter 2: Check Last Available Date
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


# Filter 3: Fetch Missing Data
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


# Filter 4: Save to CSV
def save_to_csv(data):
    if os.path.exists(CSV_FILE):
        existing_data = pd.read_csv(CSV_FILE)
        combined_data = pd.concat([existing_data, pd.DataFrame(data)], ignore_index=True)
    else:
        combined_data = pd.DataFrame(data)

    combined_data.drop_duplicates(subset=['company_name', 'date'], inplace=True)
    combined_data.to_csv(CSV_FILE, index=False, encoding='utf-8')
    print(f"Data saved to '{CSV_FILE}'")


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

        save_to_csv(all_data)
    end_time = time.time()
    print(f"Data fetching and processing completed in {end_time - start_time:.2f} seconds.")


if __name__ == '__main__':
    asyncio.run(main())

