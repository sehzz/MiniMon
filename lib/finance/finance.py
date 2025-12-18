import json
# from datetime import datetime
from datetime import datetime, timedelta, timezone

from lib.finance.entites import Transaction
from lib.utils.connectors import URLCaller
from lib.utils.cache import JSONFileCache
from lib.utils.environment import get_conf_for, is_server
from lib.utils.token_handler import get_token_from_cache, save_token_to_file
from config import KEY_DIR
from lib.utils.log import logger

log = logger.get_logger()

MONMINI_TOKEN_PATH = KEY_DIR.joinpath("monmimi_access_token_60_min")
MONMINI_TOKEN_KEY = "monmimi_access_token"


def get_acces_token() -> str:
    """
    Get access token for API calls, using cached token if valid. Otherwise, fetch a new token and cache it.

    Returns:
        str: Access token.
    """
    if get_token_from_cache(MONMINI_TOKEN_KEY):
        log.debug("Using cached access token.")
        return get_token_from_cache(MONMINI_TOKEN_KEY)

    log.debug("Fetching new access token from Supabase.")

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
    token = data.get("access_token")

    save_token_to_file(MONMINI_TOKEN_KEY, 60 * 60, token)
    
    return data["access_token"]

def get_transaction_data() -> None:
    """
    Fetch transaction data from database and cache it.

    Returns:
        None
    """
    conf = get_conf_for("supabase")
    base_url = conf.get("base_url")

    url = f"{base_url}/rest/v1/new_transactions"
    api_key = conf.get("api_key")

    token = get_acces_token()

    headers = {
        "apikey": api_key,
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    url_caller = URLCaller(headers=headers)
    result = url_caller.perform_single_call(url=url, verb="get")
    data = result.json
    cache = JSONFileCache(name="transaction_data.json")
    cache.save(data) 

def get_current_week_data():
    """Get transactions from the current week (Monday to Sunday)."""

    cache = JSONFileCache(name="transaction_data.json")

    if not cache.is_valid:
        log.debug("Cache is old, fetching new transaction data.")
        get_transaction_data()
        
    transaction_data = cache.retreive().get("data")

    items_this_week = []
    now = datetime.now(timezone.utc)
    # now = datetime(2025, 10, 28, 21, 58, 19, tzinfo=timezone.utc)
    days_since_monday = now.weekday()
    start_of_week = now - timedelta(days=days_since_monday)
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_week = start_of_week + timedelta(days=7)

    for item in transaction_data:
        data = Transaction(**item)
        created_at_dt = datetime.strptime(data.created_at, "%Y-%m-%dT%H:%M:%S.%f%z")
        if start_of_week <= created_at_dt < end_of_week:
            items_this_week.append(data)

    return items_this_week
   

if __name__ == "__main__":
    get_acces_token()
    # get_transaction_data()
    # get_current_week_data()