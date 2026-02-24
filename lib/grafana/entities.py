from datetime import datetime, timedelta, timezone

from pydantic import BaseModel

from lib.database.entities import Database
from lib.utils.environment import get_conf_for
from lib.utils.log import logger

log = logger.get_logger()

class GrafanaData(BaseModel):
    id: int
    timestamp: str
    payload: dict
    service_name: str

    def is_older_than_n_days(self, days: int = 2) -> bool:
        """Determines if this specific instance is older than N days."""
        try:
            dt_str = self.timestamp.replace("+00", "+0000")
            dt_object = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S.%f%z")
        except ValueError:
            dt_object = datetime.fromisoformat(self.timestamp.replace("+00", "+00:00"))
            
        return (datetime.now(timezone.utc) - dt_object) >= timedelta(days=days)

class Grafana:
    """
    Grafana entity to interact with Grafana database.
    
    dashboard_name (str): Name of the Grafana dashboard.
    """
    def __init__(self, dashboard_name: str):
        self.dashboard_name = dashboard_name
        self.app_name = "grafana_db"
        self.db = Database(app_name=self.app_name)
        self.conf = get_conf_for(self.app_name)

    def add_data(self, data):
        """
        data (dict): The data to be added to the table.
                        Example: {
                        "some_column": "someValue",
                        "other_column": "otherValue"
                        }
        """
        table_name = self.conf.get("table_name")
        if not table_name:
            log.error("Table name not found in config")
            return None
        self.db.insert_data_to_table(table_name, data)

    def fetch_data(self):
        "Fetch all data entries from the Grafana database table."

        table_name = self.conf.get("table_name")
        if not table_name:
            log.error("Table name not found in config")
            return None
        return self.db.get_data_from_table(table_name)
    
    def delete_data(self, id: int):
        """
        Delete a specific data entry from the Grafana database table based on its ID.
        
        Args:
            id (int): The unique identifier of the data entry to be deleted.

        Returns:
            None
        """
        table_name = self.conf.get("table_name")
        if not table_name:
            log.error("Table name not found in config")
            return None
        log.info(f"Processing deletion for id: {id}")
        self.db.delete_data_from_table(table_name, id)

    def old_entry_cleanup(self):
        "Delete Grafana data entries older than 2 days."
        
        table_data = []
        data = self.fetch_data()
        for i in data:
            table_data.append(GrafanaData(**i))
        
        if GrafanaData.is_older_than_n_days:
            self.delete_data(id=GrafanaData.id)

        