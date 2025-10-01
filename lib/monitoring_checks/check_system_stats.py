import psutil
from lib.service.Service import ServiceEntry, Service_Status, Service_PerformanceData

from lib.service.spool_generator import generate_service_response, write_spool_file
from lib.utils.environment import get_conf_for, is_server
from lib.utils.log import logger

log = logger.get_logger()

def run():
    """Run the health check and write the spool file."""    

    conf = get_conf_for("system_stats")
    stats = check_system_stats(conf)
    spool_string = generate_service_response(
            service_data= stats,
            host_name=conf.get("host_name", "unknown_host")
        )
    if is_server():
        write_spool_file("health_check", spool_string, 5)
    else:
        log.info(f"Spool string:\n{spool_string}")



def check_system_stats(conf: dict):
    """Check system statistics like CPU, memory, and disk usage."""

    entries = []
    service_name = conf.get("server_name")
    states_entries = {
        "cpu": psutil.cpu_percent(),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent
    }

    for name, stat in states_entries.items():
        if stat > conf.get(f"{name}_threshold"):
            entries.append(
                ServiceEntry(
                    service_name=service_name.replace("stats", name),
                    status_id=Service_Status.WARNING,
                    status_message=f"{name} usage is high: {stat}",
                    performance=[Service_PerformanceData(label=f"{name}_usage", value=stat)]
                )
            )
        else:
            entries.append(
                ServiceEntry(
                    service_name=service_name.replace("stats", name),
                    status_id=Service_Status.OK,
                    status_message=f"{name} stats collected successfully",
                    performance=[Service_PerformanceData(label=f"{name}_usage", value=stat)]
                )
            )

    return entries
    
    
    

    



    return







if __name__ == "__main__":
    run()