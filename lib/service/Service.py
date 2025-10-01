from enum import Enum
from typing import Optional, List, Union, Sequence, Any
from datetime import datetime
from pydantic import BaseModel


class Service_Status(int, Enum):
    """
    Enumeration for service status levels.

    Values:
        OK: Service is operating normally.  Value 0.
        WARNING: Service is experiencing issues but is still operational.  Value 1.
        CRITICAL: Service is down or not functioning.  Value 2.
        UNKNOWN: Service status is unknown.  Value 3.
    """
    OK = 0
    WARNING = 1
    CRITICAL = 2
    UNKNOWN = 3

class Service_PerformanceData(BaseModel):
    label: str
    value: object #Union[Service_Status, float, int, str, Sequence[Any]]
    warn: object = ''
    crit: object = ''
    min: object = ''
    max: object = ''

    @property
    def as_spool_str(self):
        """Transform the performance data to a string suitable for monitoring spool files."""

        if isinstance(self.value, Service_Status):
            self.value = self.value.value
        
        values = (self.value, self.warn, self.crit, self.min, self.max)
        rhs = ";".join([str(v) for v in values])
        
        label = self.label.replace(" ", "_")
        # rhs = ";".join(parts)

        return f"{label}={rhs}"

class ServiceEntry(BaseModel):
    service_name: str
    status_id: Service_Status = Service_Status.UNKNOWN
    status_message: str = "Service status unknown"
    last_checked: datetime = datetime.now()
    performance: Optional[List[Service_PerformanceData]] = None

    @property
    def as_spool_str(self):
        """"Transform the service entry to a string suitable for monitoring spool files."""

        status = self.status_id
        if isinstance(self.status_id, Service_Status):
            status = self.status_id.value
        
        service = self.service_name.replace(" ", "_")

        if not self.performance:
            performance = "-"

        else:
            performance = '|'.join([pe.as_spool_str for pe in self.performance])

        msg = self.status_message

        return f"{status} {service} {performance} {msg}"