import json
# from datetime import datetime
from datetime import datetime, timedelta, timezone

from lib.finance.entites import Transaction
from lib.utils.connectors import URLCaller
from lib.utils.cache import JSONFileCache
from lib.utils.environment import get_conf_for, is_server
from config import KEY_DIR
from lib.utils.log import logger

log = logger.get_logger()

TOKEN_PATH = KEY_DIR.joinpath("sehaj_access_token_60_min")
MONMINI_TOKEN_PATH = KEY_DIR.joinpath("monmimi_access_token_60_min")



def get_acces_token():
    conf = get_conf_for("supabase")
    base_url = conf.get("base_url")
    access_token_endpoint = conf.get("access_token_endpoint")
    url = f"{base_url}/{access_token_endpoint}"
    api_key = conf.get("api_key")

    headers = {
        "apikey": api_key,
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    email = conf.get("email")
    password = conf.get("password")
    body = {
        "email": email,
        "password": password
    }

    url_caller = URLCaller(headers=headers)
    result = url_caller.perform_single_call(url=url, verb="post", json= body)
    data = result.json
    cache = JSONFileCache(name="monmimi_access_token_60_min")
    cache.save(data["access_token"], is_key=True)
    
    return data["access_token"]


def get_transaction_data():
    conf = get_conf_for("supabase")
    base_url = conf.get("base_url")

    url = f"{base_url}/rest/v1/new_transactions"
    api_key = conf.get("api_key")

    token = JSONFileCache(name="monmimi_access_token_60_min")
    token_data = token.retreive(is_key=True).get("data")


    headers = {
        "apikey": api_key,
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token_data}"
    }

    url_caller = URLCaller(headers=headers)
    result = url_caller.perform_single_call(url=url, verb="get")
    data = result.json
    get_current_week_data(data)
    

def get_current_week_data(data):
    """Get transactions from the current week (Monday to Sunday)."""

    # now = datetime(2025, 10, 28, 21, 58, 19, tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    days_since_monday = now.weekday()
    start_of_week = now - timedelta(days=days_since_monday)
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_week = start_of_week + timedelta(days=7)

    print(f"Current Week Range:")
    print(f"- Start (Mon): {start_of_week.isoformat()}") # 2025-11-03T00:00:00+00:00
    print(f"- End (Next Mon): {end_of_week.isoformat()}") # 2025-11-10T00:00:00+00:00
    print("-" * 30)


    items_this_week = []
    cache = JSONFileCache(name="transaction_data.json")
    data_list = data
    for item in data_list:
        try:
            created_at_dt = datetime.strptime(item["created_at"], "%Y-%m-%dT%H:%M:%S.%f%z")

            if start_of_week <= created_at_dt < end_of_week:
                items_this_week.append(item)

        except ValueError as e:
            print(f"Skipping item {item.get('id', 'N/A')} due to parsing error: {e}")
    
    log.debug(items_this_week)
    cache.save(items_this_week)




if __name__ == "__main__":
    # get_acces_token()
    get_transaction_data()