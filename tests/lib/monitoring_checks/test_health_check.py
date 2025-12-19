from unittest.mock import Mock
from lib.service.Service import Service_Status
from lib.monitoring_checks.health_check import health_check
from tests.lib.factories.faktory import URLCallerResultFactory
from tests.utilities import HCPyTest
from fastapi import status as http_status

LIB_PATH = "lib.monitoring_checks.health_check"


class TestHealthCheck(HCPyTest):
    PATCH_STRINGS = [
        "URLCaller",
    ]

    def test_health_check_ok(self):
        mock_conf = {"health_url": "something"}
        mock_response = {
            "status": "ok",
            "uptime": 12345
        }
        fake_caller = Mock()
        fake_caller.perform_single_call.return_value = URLCallerResultFactory(
            with_payload=mock_response,
            with_status_code=http_status.HTTP_200_OK
        )
        self.mocks["URLCaller"].return_value = fake_caller

        result = health_check(mock_conf)

        assert result.status_id == Service_Status.OK
        assert result.status_message == "Service is running fine."
        assert len(result.performance) == 1
        assert result.performance[0].label == "uptime"
        assert result.performance[0].value == 12345
