import inspect
import json
from pathlib import Path
import tempfile
from unittest.mock import patch

from pydantic import BaseModel, StrictBytes, StrictStr
from typing import List, Optional, Union
from fastapi import status as http_status


class MockResponse(BaseModel):
    """A mock response object to simulate HTTP responses in tests."""

    payload: Union[list, dict] = {}
    status_code: int = http_status.HTTP_200_OK
    content: Union[StrictBytes, StrictStr] = ""
    text: str = ""
    header: dict = {}
    reason: str = ""

    def json(self):
        return self.payload
    
    @property
    def body(self):
        return json.dumps(self.payload)

    
class HCPyTest:
    """Base class for health check tests, providing setup and teardown methods."""

    TESTED_LIB = None
    PATCH_STRINGS = None

    def setup_method(self):
        """Set up the test environment, including patches and temporary directory."""

        module = inspect.getmodule(self)
        try:
            self.TESTED_LIB = self.TESTED_LIB or module.LIB_PATH
        except AttributeError:
            msg = (
                f"TESTED_LIB is not provided,so we tried to use LIB_PATH from {module.__name__},"
                "but it is not defined!"
            )
            raise AttributeError(msg)
        
        # self._tmp_dir = tempfile.TemporaryDirectory()
        self._tmp = tempfile.TemporaryDirectory()
        # self._tmp_dir = Path(self._tmp_dir.name)
        self._tmp_dir = Path(self._tmp.name)
        self.patches = {}
        self.mocks = {}
        for string in (self.PATCH_STRINGS or []):
            if isinstance(string, str):
                name = string.split(".")[-1]
                string = name, string
            name, path = string

            if "." not in path and self.TESTED_LIB is not None:
                path = f"{self.TESTED_LIB}.{path}"
            self.patches[name] = patch(path)
            self.mocks[name] = self.patches[name].start()
    
    def teardown_method(self):
        """Stop all patches and clean up temporary directory."""

        self._tmp.cleanup()
        for p in self.patches.values():
            p.stop()
            