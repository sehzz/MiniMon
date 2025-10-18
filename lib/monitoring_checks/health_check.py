from lib.utils.connectors import URLCaller
from lib.utils.environment import get_conf_for, is_server
from lib.service.Service import Service_Status, ServiceEntry, Service_PerformanceData
from lib.service.spool_generator import generate_service_response, write_spool_file
from lib.utils.log import logger

log = logger.get_logger()

def run():
    """Run the health check and write the spool file."""    
    spool_strings = []
    confs = ["expense_tracker", "home_smart_home"]
    for conf in confs:
        conf = get_conf_for(conf)
        entry = health_check(conf)

        spool_string = generate_service_response(
            service_data= [entry],
            host_name=conf.get("host_name", "unknown_host")
        )
        spool_strings.append(spool_string)

    spool_string = "".join(spool_strings)

    if is_server():
        write_spool_file("health_check", spool_string, 5)
    else:
        log.info(f"Spool string:\n{spool_string}")



def health_check(conf: dict) -> ServiceEntry:
    """Perform a health check on the expense tracker service."""

    entry = ServiceEntry(
        service_name="Expense_health_check",
    )
    url = conf.get("health_url")
    url_caller = URLCaller()

    try:
        result = url_caller.perform_single_call(url=url, verb="get")
    except ConnectionError as e:
        log.error(f"ConnectionError: {e}")
        entry.status_id = Service_Status.CRITICAL
        entry.status_message = f"ConnectionError: {e}"
        return entry
    
    if result.response.status_code != 200:
        log.error(f"Health check failed with status code: {result.response.status_code}")
        entry.status_id = Service_Status.CRITICAL
        entry.status_message = ""f"Health check failed with status code: {result.response.status_code}"
        return entry
    
    result = result.json
    status = result.get("status")
    up_time = result.get("uptime")
    performance = Service_PerformanceData(label="uptime", value=up_time)

    if status == "ok":
        entry.status_id = Service_Status.OK
        entry.status_message = "Service is running fine."
        entry.performance = [performance]
        return entry

    else:
        entry.status_id = Service_Status.CRITICAL
        log.error(f"Service status: {status}")
        entry.status_message = f"Service status: {status}"        
        return entry
    


if __name__ == "__main__":
    # health_check()
    run()
