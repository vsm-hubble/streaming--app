import yfinance as yf
import json

def fetch_commodity_data(commodity_names: list[str]):
    """
    Fetches commodity data using the yfinance library.

    Args:
        commodity_names (list[str]): A list of commodity names to fetch data for.
                                     The function will map these names to their
                                     Yahoo Finance ticker symbols internally.
    Returns:
        dict: A dictionary containing the scraped data for each commodity,
              or an error message if the request fails.
    """
    TARGET_COMMODITIES = {
        "gold": "GC=F",
        "silver": "SI=F",
        "copper": "HG=F",
        "natural gas": "NG=F",
        "brent crude": "BZ=F",
        "crude oil": "CL=F"
    }
    commodity_data = {}
    print("Fetching data using yfinance...")

    for name in commodity_names:
        ticker = TARGET_COMMODITIES.get(name.lower())
        if not ticker:
            commodity_data[name] = {"error": f"Unknown commodity name: '{name}'."}
            print(f"  - WARNING: {commodity_data[name]['error']}")
            continue

        try:
            ticker_data = yf.Ticker(ticker)
            info = ticker_data.info

            if info:
                data_entry = {}
                data_entry['name'] = name
                data_entry['symbol'] = ticker
                data_entry['price'] = info.get("regularMarketPrice", "N/A")
                data_entry['change'] = info.get("regularMarketChange", "N/A")
                data_entry['change_percent'] = info.get("regularMarketChangePercent", "N/A")
                commodity_data[name] = data_entry
                print(f"  - Found data for {name}")
            else:
                commodity_data[name] = {"error": f"Could not retrieve data for commodity '{name}' with ticker '{ticker}'."}
                print(f"  - WARNING: {commodity_data[name]['error']}")
        except Exception as e:
            commodity_data[name] = {"error": f"Failed to fetch data for {name} ({ticker}): {e}"}
            print(f"  - ERROR: {commodity_data[name]['error']}")

    return commodity_data

if __name__ == "__main__":
    # URL for Yahoo Finance's commodities page
    # YAHOO_URL is now defined inside the function, no longer needed here
    
    # Dictionary of the commodities we want to scrape, mapping name to Yahoo Finance ticker
    # TARGET_COMMODITIES = {
    #     "gold": "GC=F",
    #     "silver": "SI=F",
    #     "copper": "HG=F",
    #     "natural gas": "NG=F",
    #     "brent crude": "BZ=F",
    #     "crude oil": "CL=F"
    # }
    
    print("Starting commodity data fetch...")
    # The URL parameter is no longer directly used in the API call within the function
    # but it's kept for function signature compatibility for now.
    scraped_info = fetch_commodity_data(["gold", "silver", "copper", "natural gas", "brent crude", "crude oil"])

    print("\n--- Scraped Commodity Futures Data ---")
    if "error" in scraped_info:
        print(json.dumps({"error": scraped_info["error"]}))
    else:
        # Convert the dictionary of dictionaries to a list of dictionaries
        output_list = [data for data in scraped_info.values()]
        print(json.dumps(output_list, indent=2))
