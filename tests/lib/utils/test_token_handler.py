import time
from unittest.mock import patch
from lib.utils.token_handler import get_token_from_cache, get_latest_token_file_for_app, save_token_to_file, is_token_file_valid
from tests.utilities import HCPyTest

LIB_PATH = "lib.utils.token_handler"

class TestGetTokenFromCache(HCPyTest):
    PATCH_STRINGS = ["get_latest_token_file_for_app", "is_token_file_valid"]

    def test_successful_token_retrieval(self):
        """Test that a valid token is read and returned correctly."""

        token_name = "test_app"
        expected_token = "cached_token_value"
        
        token_file = self._tmp_dir / "test_app_expires_at_1234567890"
        token_file.write_text(expected_token, encoding="utf-8")

        self.mocks["get_latest_token_file_for_app"].return_value = token_file
        self.mocks["is_token_file_valid"].return_value = True

        result = get_token_from_cache(token_name, self._tmp_dir)

        assert result == expected_token
        self.mocks["get_latest_token_file_for_app"].assert_called_once_with(token_name, self._tmp_dir)
        self.mocks["is_token_file_valid"].assert_called_once_with(token_file)


    def test_invalid_token_file(self, log):
        """Test that an invalid token file results in None and deletion of the file."""

        token_name = "test_app"
        expected_token = "cached_token_value"
        
        token_file = self._tmp_dir / "test_app_expires_at_1234567890"
        token_file.write_text(expected_token, encoding="utf-8")

        self.mocks["get_latest_token_file_for_app"].return_value = token_file
        self.mocks["is_token_file_valid"].return_value = False

        result = get_token_from_cache(token_name, self._tmp_dir)

        assert result is None
        log.info.assert_called_once_with(f"Token for {token_name} has expired. Deleting token file.")
        self.mocks["get_latest_token_file_for_app"].assert_called_once_with(token_name, self._tmp_dir)
        self.mocks["is_token_file_valid"].assert_called_once_with(token_file)

    def test_no_token_file_found(self, log):
        """Test that None is returned when no token file is found."""

        self.mocks["get_latest_token_file_for_app"].return_value = None
        token_name = "test_app"
        
        self._tmp_dir / "test_app_expires_at_1234567890"

        assert get_token_from_cache(token_name, self._tmp_dir) is None
        log.warning.assert_called_once_with(f"No cached token found for {token_name}")


class TestGetLatestTokenFileForApp(HCPyTest):
    def test_success(self):
        """Test that the function returns the most recently modified token file."""

        token_name = "test_app"
        expected_token = "cached_token_value"
        
        token_file = self._tmp_dir / "test_app_expires_at_1234567890"
        token_file.write_text(expected_token, encoding="utf-8")

        result = get_latest_token_file_for_app(token_name, self._tmp_dir)

        assert result == token_file

    def test_no_dir_found(self):
        """Test that the function returns None when the directory does not exist."""

        token_name = "test_app"
        fake_dir = self._tmp_dir / "non_existent_folder"
        
        get_latest_token_file_for_app(token_name, fake_dir) is None


    def test_no_file_found_in_dir(self):
        """Test that the function returns None when no matching token files are found."""

        token_name = "test_app"

        token_file = self._tmp_dir / "wrong_name_pattern"
        token_file.write_text("data", encoding="utf-8")

        get_latest_token_file_for_app(token_name, self._tmp_dir) is None

    def test_uses_default_key_dir_when_arg_is_none(self):
        """Test that the function falls back to KEY_DIR when no directory is provided."""

        token_name = "default_app"
        token_file = self._tmp_dir / "default_app_expires_at_9999"
        token_file.write_text("content", encoding="utf-8")

        with patch(f"{LIB_PATH}.KEY_DIR", self._tmp_dir):
            assert get_latest_token_file_for_app(token_name) == token_file


    class TestSaveTokenToFile(HCPyTest):
        def test_success_run(self):
            token_name = "test_app"
            expected_token = "cached_token_value"
            
            token_file = self._tmp_dir / "test_app_expires_at_1234567890"
            token_file.write_text(expected_token, encoding="utf-8")

            assert save_token_to_file(token=expected_token, ttl_seconds=1, token_name=token_name, token_dir=self._tmp_dir) is None

        def test_uses_default_key_dir_when_arg_is_none(self):
            """Test that the function falls back to KEY_DIR when no directory is provided."""

            token_name = "default_app"
            expected_token = "cached_token_value"
            token_file = self._tmp_dir / "default_app_expires_at_9999"
            token_file.write_text("content", encoding="utf-8")

            with patch(f"{LIB_PATH}.KEY_DIR", self._tmp_dir):
                assert save_token_to_file(token=expected_token, ttl_seconds=1, token_name=token_name) is None

        def test_raise_exception_on_file_write(self, log):
            """Test that an exception during file write is handled gracefully."""

            token_name = "test_app"
            
            with patch("pathlib.Path.replace", side_effect=Exception("Permission Denied")):
                save_token_to_file(token_name, 1, "token", self._tmp_dir)
            
            log.error.assert_called_once_with(f"Failed to write token for {token_name}: Permission Denied")
            temp_files = list(self._tmp_dir.glob("*.tmp"))
            assert len(temp_files) == 0


class TestIsTokenFileValid(HCPyTest):
    def test_valid_token_file(self):
        """Test that a valid (non-expired) token file is recognized as valid."""

        future_timestamp = int(time.time()) + 3600
        token_file = self._tmp_dir / f"test_app_expires_at_{future_timestamp}"
        token_file.write_text("valid_token", encoding="utf-8")

        assert is_token_file_valid(token_file) is True

    def test_expired_token_file(self):
        """Test that an expired token file is recognized as invalid."""

        past_timestamp = int(time.time()) - 3600
        token_file = self._tmp_dir / f"test_app_expires_at_{past_timestamp}"
        token_file.write_text("expired_token", encoding="utf-8")

        assert is_token_file_valid(token_file) is False

    def test_malformed_token_file_name(self):
        """Test that a token file with a malformed name is recognized as invalid."""

        token_file = self._tmp_dir / "test_app_invalid_format"
        token_file.write_text("some_token", encoding="utf-8")

        assert is_token_file_valid(token_file) is False