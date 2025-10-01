from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
LOG_FILE_PATH = BASE_DIR / "app.log"
SETTINGS_PATH = BASE_DIR / "conf" / "Settings.json"
SERVICE_SPOOL_PATH = Path("/var/spool/monitoring")
