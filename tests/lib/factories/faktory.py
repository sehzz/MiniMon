from unittest.mock import Mock
from factory import Factory, post_generation

from lib.utils.connectors import URLCallerResult
from tests.utilities import MockResponse


class HCFactory(Factory):
    """A factory for creating health check monitor instances for testing."""

    @post_generation
    def with_default(self, create: bool, extracted: None, **kwargs):
        """Set default attributes for the health check monitor instance."""

        for arg, value in kwargs.items():
            if value is True:
                delattr(self, arg)
    
    @post_generation
    def with_attribute(obj, create: bool, extracted: None, **kwargs):
        """Set attributes for the health check monitor instance."""

        for method_name, value in kwargs.items():
            object.__setattr__(obj, method_name, value)
    
    @post_generation
    def with_method(obj, create: bool, extracted: None, **kwargs):
        """Set methods for the health check monitor instance."""

        for method_name, value in kwargs.items():
            if method_name.endswith("__return"):
                method_name = method_name.replace("__return", "")
                value = Mock(return_value=value)

            if method_name.endswith("__side_effect"):
                method_name = method_name.replace("__side_effect", "")
                value = Mock(side_effect=value)
            
            object.__setattr__(obj, method_name, value)


class URLCallerResultFactory(HCFactory):

    response = None

    class Meta:
        model = URLCallerResult

    @post_generation
    def with_content(self, create: bool, extracted: None, **kwargs):
        """Set content to the fake response."""

        if extracted is None:
            return
        
        if self.response is None:
            self.response = MockResponse()
        
        self.response.content = extracted

    @post_generation
    def with_payload(self, create: bool, extracted: None, **kwargs):
        """Set payload to the fake response."""

        if extracted is None:
            return
        
        if self.response is None:
            self.response = MockResponse()
        
        self.response.payload = extracted

    @post_generation
    def with_status_code(self, create: bool, extracted: None, **kwargs):
        """Set HTTP status_code on the fake response."""

        if extracted is None:
            return
        if self.response is None:
            self.response = MockResponse()
        self.response.status_code = extracted