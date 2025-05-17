import json
import os
from datetime import date, timedelta

from ansi import ansi

TOKEN_DB_FILE = "token_usage.json"

def load_token_data():
    """Loads token usage data from a JSON file."""
    if not os.path.exists(TOKEN_DB_FILE):
        return {"total": 0, "daily": {}}
    try:
        with open(TOKEN_DB_FILE, 'r') as f:
            data = json.load(f)
            # Ensure structure is correct
            if "total" not in data or "daily" not in data:
                print(ansi.WARNING_MSG + f"{TOKEN_DB_FILE} structure incorrect. Resetting.")
                return {"total": 0, "daily": {}}
            return data
    except json.JSONDecodeError:
        print(ansi.ERROR_MSG + f"Error decoding JSON from {TOKEN_DB_FILE}. Resetting.")
        return {"total": 0, "daily": {}}
    except Exception as e:
        print(ansi.ERROR_MSG + f"Error loading token data from {TOKEN_DB_FILE}: {e}. Resetting.")
        return {"total": 0, "daily": {}}

def save_token_data(data):
    """Saves token usage data to a JSON file."""
    try:
        with open(TOKEN_DB_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(ansi.ERROR_MSG + f"Error saving token data to {TOKEN_DB_FILE}: {e}")

def update_token_data(data, tokens_used):
    """Updates token usage data with new tokens used."""
    if tokens_used is None or not isinstance(tokens_used, int) or tokens_used < 0:
        print(ansi.WARNING_MSG + f"Invalid token usage value received: {tokens_used}. Not updating.")
        return data # Return data unchanged

    today_str = str(date.today())

    data["total"] += tokens_used
    data["daily"][today_str] = data["daily"].get(today_str, 0) + tokens_used

    # Prune old daily data (older than 30 days)
    prune_date = date.today() - timedelta(days=30)
    keys_to_prune = [d for d in data["daily"] if date.fromisoformat(d) < prune_date]
    for k in keys_to_prune:
       del data["daily"][k]

    return data

# Example Usage:
# token_data = load_token_data()
# print(f"Loaded initial data: {token_data}")
# token_data = update_token_data(token_data, 150) # Example tokens used
# print(f"Updated data: {token_data}")
# save_token_data(token_data)