#
# tradingview_scraper.py
#
# This script is designed to be a tool for an agentic AI model.
# It scrapes market mover data from TradingView and returns it in a structured format.
#
# Requirements:
# - requests: For making HTTP requests to the website.
# - beautifulsoup4: For parsing the HTML content.
#
# You can install these with pip:
# pip install requests beautifulsoup4
#

import requests
from bs4 import BeautifulSoup
import json

def _parse_market_cap(market_cap_str: str) -> float:
    """
    Helper function to parse market cap strings (e.g., '1.23T', '45.67B', '123.45M')
    into a numerical float value.
    """
    if not market_cap_str:
        return 0.0

    market_cap_str = market_cap_str.replace('$', '').strip()
    multiplier = 1.0
    if market_cap_str.endswith('T'):
        multiplier = 1_000_000_000_000.0
        market_cap_str = market_cap_str[:-1]
    elif market_cap_str.endswith('B'):
        multiplier = 1_000_000_000.0
        market_cap_str = market_cap_str[:-1]
    elif market_cap_str.endswith('M'):
        multiplier = 1_000_000.0
        market_cap_str = market_cap_str[:-1]
    elif market_cap_str.endswith('K'):
        multiplier = 1_000.0
        market_cap_str = market_cap_str[:-1]

    try:
        return float(market_cap_str) * multiplier
    except ValueError:
        return 0.0

def scrape_tradingview_market_movers(url: str = "https://www.tradingview.com/markets/stocks-usa/market-movers-large-cap/") -> str:
    """
    Scrapes the top 100 large-cap stocks from TradingView's market movers page.

    This function is designed to be a tool for an agentic AI model. It takes a URL,
    fetches the HTML, and parses the stock data into a JSON string. The agent can then
    process this structured data to answer user queries about market performance.

    Args:
        url (str): The URL of the TradingView market movers page.
                   Defaults to the large-cap market movers page.

    Returns:
        str: A JSON formatted string containing a list of dictionaries. Each dictionary
             represents a stock and its key metrics. Returns an error message as a string
             if the scraping process fails.
    """
    try:
        # Use a User-Agent header to mimic a web browser and avoid being blocked.
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # Fetch the HTML content of the page.
        response = requests.get(url, headers=headers, timeout=15)
        # Raise an exception for bad status codes (4xx or 5xx).
        response.raise_for_status()

        # Parse the HTML content using BeautifulSoup.
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the table containing the market data.
        # The data is typically within a div with a specific data-tv-dataset-id,
        # but the table structure is more reliable for direct scraping.
        # We look for a table with a data-tv-entity-col-grouping="true" attribute.
        # If that fails, we'll try a more general approach.
        data_table = soup.find('table')

        if not data_table:
            return "Error: Could not find any table on the page."

        # Find all table rows (tr) within the table body (tbody).
        rows = data_table.find('tbody')

        if not rows:
            return "Error: Could not find tbody in the table."

        rows = rows.find_all('tr')

        if not rows:
            return "Error: Could not find any stock data rows."

        stock_data = []
        # Iterate over each row to extract the stock information.
        for row in rows:
            # Find all table data cells (td) in the current row.
            cells = row.find_all('td')
            
            # Ensure the row has the expected number of cells to avoid errors.
            if len(cells) < 12:
                continue

            # Extract the data from each cell.
            # The first cell contains both the ticker and the name.
            symbol_cell_content = cells[0].get_text(separator=' ', strip=True)
            # Attempt to split the ticker and name. Ticker is usually the first word.
            parts = symbol_cell_content.split(' ', 1)
            ticker = parts[0] if parts else ''
            name = parts[1] if len(parts) > 1 else ''

            market_cap = cells[1].get_text(strip=True)
            price = cells[2].get_text(strip=True)
            change_percent = cells[3].get_text(strip=True)
            volume = cells[4].get_text(strip=True)
            rel_volume = cells[5].get_text(strip=True)
            p_e_ratio = cells[6].get_text(strip=True)
            eps_dil_ttm = cells[7].get_text(strip=True)
            eps_dil_growth_ttm_yoy = cells[8].get_text(strip=True)
            div_yield_percent_ttm = cells[9].get_text(strip=True)
            sector = cells[10].get_text(strip=True)
            analyst_rating = cells[11].get_text(strip=True)

            # Create a dictionary for the stock's data.
            stock_info = {
                'ticker': ticker,
                'name': name,
                'market_cap': market_cap,
                'price': price,
                'change_percent': change_percent,
                'volume': volume,
                'rel_volume': rel_volume,
                'p_e_ratio': p_e_ratio,
                'eps_dil_ttm': eps_dil_ttm,
                'eps_dil_growth_ttm_yoy': eps_dil_growth_ttm_yoy,
                'div_yield_percent_ttm': div_yield_percent_ttm,
                'sector': sector,
                'analyst_rating': analyst_rating,
                '_parsed_market_cap': _parse_market_cap(market_cap) # Add parsed market cap for sorting
            }
            stock_data.append(stock_info)

        # Sort the stock_data by market_cap in descending order and take the top 10.
        stock_data_sorted = sorted(stock_data, key=lambda x: x.get('_parsed_market_cap', 0.0), reverse=True)
        top_10_market_movers = stock_data_sorted[:10]

        # Convert the list of dictionaries to a JSON formatted string.
        # This is a good format for an agent to consume.
        return json.dumps(top_10_market_movers, indent=4)

    except requests.exceptions.RequestException as e:
        # Handle network-related errors gracefully.
        return f"Error during web request: {e}"
    except Exception as e:
        # Handle any other unexpected errors.
        return f"An unexpected error occurred: {e}"

# Example of how an agent might call this function.
if __name__ == "__main__":
    print("Scraping TradingView large-cap market movers...")
    scraped_data = scrape_tradingview_market_movers()
    
    # In a real agent, this data would be passed back to the LLM for analysis.
    if scraped_data.startswith("Error"):
        print(scraped_data)
    else:
        # For demonstration, we'll parse and print the top 10 results.
        data_list = json.loads(scraped_data)
        print("Successfully scraped data for", len(data_list), "stocks.")
        print("\nTop 10 stocks:")
        print(json.dumps(data_list, indent=4))
