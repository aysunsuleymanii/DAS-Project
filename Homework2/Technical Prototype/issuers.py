import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re

BASE_URL = 'https://www.mse.mk/en/stats/symbolhistory/'
CSV_FILE = 'stock_data.csv'


# Filter 1: Extract Issuers with filtering based on condition
async def extract_issuers(session):
    url = 'https://www.mse.mk/en/stats/current-schedule'

    async with session.get(url) as response:
        if response.status != 200:
            print("Failed to fetch the webpage.")
            return []

        soup = BeautifulSoup(await response.text(), 'html.parser')

        tab_ids = [
            'results-continuousTradingMode',
            'results-fixingWith20PercentLimit',
            'results-fixingWithoutLimit'
        ]

        issuers = []

        for tab_id in tab_ids:
            tab_content = soup.find('div', {'id': tab_id})

            if tab_content:
                table = tab_content.find('table')

                if table:
                    rows = table.find_all('tr')

                    for row in rows:
                        symbol_cell = row.find('a', href=True)
                        if symbol_cell:
                            issuer_name = symbol_cell.text.strip()

                            if not (issuer_name[0] in 'EMS' or re.search(r'\d', issuer_name)):
                                issuers.append(issuer_name)

        return issuers


async def main():
    async with aiohttp.ClientSession() as session:
        issuers = await extract_issuers(session)

        # Print each issuer on a new line
        print("Filtered Issuers:")
        for issuer in issuers:
            print(issuer)


if __name__ == '__main__':
    asyncio.run(main())
