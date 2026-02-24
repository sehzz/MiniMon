from lib.grafana.entities import Grafana, GrafanaData
from lib.utils.connectors import URLCaller
from lib.utils.environment import get_conf_for
from lib.utils.log import logger

log = logger.get_logger()
grafana = Grafana(dashboard_name="expense_app")


def get_headers():
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

def get_expense_app_health():
    "Fetch health status from the expense tracking application."

    conf = get_conf_for("expense_tracker")
    base_url = conf.get("base_url")
    if not base_url:
        log.error("Base URL not found in config")
        return None

    health_endpoint = conf.get("health_endpoint")
    if not health_endpoint:
        log.error("Health endpoint not found in config")
        return None

    url_caller = URLCaller(headers=get_headers())
    url = f"{base_url}{health_endpoint}"

    response = url_caller.perform_single_call(url=url, verb="get", verify=False)
    if response.response.status_code != 200:
        log.error(f"Expense app health check failed with status code: {response.response.status_code}")
        return None
    
    return response.json

def add_grafana_data():
    "Add health data of expense app to Grafana database."
    
    payload = get_expense_app_health()
    if not payload:
        return None
    
    data = {
        "payload": payload,
        "service_name": "expense_app"
    }
    grafana.add_data(data=data)
    log.debug(f"Added grafana data: {data}")


def delete_old_grafana_data():
    "Delete Grafana data older than 2 days."
    
    data_entries = grafana.fetch_data()
    if not data_entries:
        log.info("No data entries found in Grafana database.")
        return
    
    for entry in data_entries:
        grafana_data = GrafanaData(**entry)
        if grafana_data.is_older_than_n_days(days=2):
            grafana.delete_data(id=grafana_data.id)
            log.debug(f"Deleted old Grafana data with id: {grafana_data.id}")

if __name__== "__main__":
    # get_expense_app_health()
    add_grafana_data()
    delete_old_grafana_data()