from polygon import RESTClient
import datetime
import json


def _get_last_available_date():
    today = datetime.date.today()
    # Go back to yesterday initially
    current_date = today - datetime.timedelta(days=1)
    
    # Loop backwards until a weekday is found
    while current_date.weekday() > 4: # Monday is 0, Sunday is 6
        current_date -= datetime.timedelta(days=1)
    return current_date

def get_treasury_yields():
    # docs
    # https://polygon.io/docs/rest/economy/treasury-yields

    # client = RESTClient("XXXXXX") # hardcoded api_key is used
    client = RESTClient("28Q3Y6RI4mlMoadL5xBBPC11nDVoP6L4") # Replace "YOUR_POLYGON_API_KEY" with your actual key
    #client = RESTClient()  # POLYGON_API_KEY environment variable is used
    #client = RESTClient()  # Use environment variable for API key
    
    # yesterday = datetime.date.today() - datetime.timedelta(days=1)
    # yesterday_str = yesterday.strftime("%Y-%m-%d")
    
    current_date = _get_last_available_date()
    max_retries = 7 # Try up to a week back for long weekends
    retries = 0
    
    while retries < max_retries:
        date_str = current_date.strftime("%Y-%m-%d")
        treasury_yields_data_generator = client.list_treasury_yields(date=date_str)
        treasury_yields_data = list(treasury_yields_data_generator) # Convert generator to a list
        
        if treasury_yields_data:
            break # Data found, exit loop
        
        print(f"No data for {date_str}, trying previous day...")
        current_date -= datetime.timedelta(days=1)
        retries += 1
    
    if not treasury_yields_data:
        print("Could not retrieve treasury yields data after multiple attempts.")
        return json.dumps([])
    
    yields_list = []
    for item in treasury_yields_data:
        yields_list.append(item.__dict__)
    return json.dumps(yields_list, indent=4)

if __name__ == "__main__":
    yields = get_treasury_yields()
    print(yields)
