from typing import List, Optional
from lib.service.Service import ServiceEntry
from pathlib import Path
from config import SERVICE_SPOOL_PATH
from lib.utils.log import logger

log = logger.get_logger()


def generate_service_response(service_data: List[ServiceEntry], host_name) -> str:
    """Generate the content of a spool file for monitoring from a list of services."""

    lines = [f"<<<<{host_name}>>>>\n<<<local>>>"]
    for entry in service_data:
        lines.append(entry.as_spool_str)

    lines.append("<<<>>>\n<<<<>>>>\n")

    return "\n".join(lines)

def generate_spool_directory() -> None:
    """Ensure the spool directory exists."""
    if not SERVICE_SPOOL_PATH.exists():
       SERVICE_SPOOL_PATH.mkdir(parents=True, exist_ok=True)

    else:
        log.debug(f"Spool directory already exists at {SERVICE_SPOOL_PATH}")

def write_spool_file(file_name: str, content: str, interval: Optional[int] = None) -> None:
    """Write the content to a spool file for monitoring."""

    path = generate_spool_path(file_name, interval)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def generate_spool_path(file_name: str, interval_min: Optional[int]= None) -> Path:
    """Generate the full path for a spool file, optionally prefixed with an interval in seconds."""

    if interval_min:
        prefix = interval_min * 60
        file_name = f"{prefix}_{file_name}.spl"
    
    return SERVICE_SPOOL_PATH.joinpath(file_name)


if __name__ == "__main__":
    generate_spool_directory()