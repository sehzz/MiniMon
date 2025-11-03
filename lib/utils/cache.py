import json

from datetime import datetime
from pathlib import Path
from pydantic import BaseModel
from config import KEY_DIR, RESOURSES_DIR
from lib.utils.log import logger

log = logger.get_logger()

class JSONFileCache(BaseModel):
    name: str

# timestamp format: "%Y-%m-%d %H:%M:%S"

    def save(self, data, save_raw: bool = False, is_key: bool = False) -> None:
        path = RESOURSES_DIR.joinpath(self.name)
        if is_key:
            path = KEY_DIR.joinpath(self.name)
        
        
        if save_raw:
            cache_data = data

        cache_data = {
            "timestamp": datetime.now().isoformat(),
            "data": data
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=4, ensure_ascii=False)
            log.info(f"File saved in {path}")

    def retreive(self, is_key: bool = False):
        """
        Retrieve data from JSON cache file.

        Returns:
            dict: {"timestamp": str, "data": dict} if successfully loaded,
                    else {"timestamp": None, "data": None}.
        """
        timestamp = None
        content = None
        path = RESOURSES_DIR.joinpath(self.name)
        if is_key:
            path = KEY_DIR.joinpath(self.name)
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = json.load(f)["data"]
            #Todo: create a function to pass timestame
            #Todo: modify reterive to pass data and timestamp
                timestamp = "NOT IMPLEMENTED"

        except(OSError, IOError) as e:
            log.error("Failed to read cache file '%s': '%s'", path, e)

        except json.JSONDecodeError:
            log.error("Cache file '%s' is not JSON serialized", self.name)
        
        return {
                "timestamp": timestamp,
                "data": content
            }

