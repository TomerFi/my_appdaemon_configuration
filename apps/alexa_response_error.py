"""Global module for use with AppDaemon, Alexa Error Response Objects.

.. codeauthor:: Tomer Figenblat <tomer.figenblat@gmail.com>

"""
from typing import Dict, Optional, Union

import little_helpers
from alexa_request import EndpointRequest, GenericRequest


class GenericErrorResponse:
    """Object representing the base generic error response.

    Do not use directly,
    use any of the following subclassess.
    """

    def __init__(
        self,
        request_object: Union[EndpointRequest, GenericRequest],
        error_type: str,
        error_message: str,
        namespace: str = "Alexa",
        **kwargs: Optional[Dict],
    ) -> None:
        """Initialize the object."""
        self.response_header = {
            "namespace": namespace,
            "name": "ErrorResponse",
            "messageId": little_helpers.get_uuid_str(),
            "payloadVersion": "3",
        }

        if isinstance(request_object, EndpointRequest):
            self.response_header[
                "correlationToken"
            ] = request_object.correlationToken
            self.response_endpoint = {"endpointId": request_object.endpointId}
        else:
            self.response_header["correlationToken"] = ""
            self.response_endpoint = {"endpointId": ""}

        self.response_payload = {"type": error_type, "message": error_message}
        if kwargs:
            for key, value in kwargs.items():
                self.response_payload[str(key)] = str(value)

    def create_response(self) -> Dict:
        """Return the dict response."""
        return {
            "event": {
                "header": self.response_header,
                "endpoint": self.response_endpoint,
                "payload": self.response_payload,
            }
        }


class TemperatureOutOfRangeErrorResponse(GenericErrorResponse):
    """Object represnting the requested temperature is out of range error."""

    def __init__(
        self,
        request_object: EndpointRequest,
        message: str,
        min_value: Union[str, int],
        max_value: Union[str, int],
        scale: str = "CELSIUS",
    ) -> None:
        """Initialize the object."""
        kwargs = {
            "validRange": {
                "minimumValue": {"value": min_value, "scale": scale},
                "maximumValue": {"value": max_value, "scale": scale},
            }
        }

        super(TemperatureOutOfRangeErrorResponse, self).__init__(
            request_object,
            "TEMPERATURE_VALUE_OUT_OF_RANGE",
            message,
            "Alexa",
            **kwargs,
        )


class ThermostatIsOffErrorResponse(GenericErrorResponse):
    """Object represnting the requested thermostat is off error."""

    def __init__(self, request_object: EndpointRequest, message: str) -> None:
        """Initialize the object."""
        super(ThermostatIsOffErrorResponse, self).__init__(
            request_object,
            "THERMOSTAT_IS_OFF",
            message,
            "Alexa.ThermostatController",
        )


class InvalidDirectiveErrorResponse(GenericErrorResponse):
    """Object represnting the request"s directive is invalid error."""

    def __init__(self, request_object: GenericRequest, message: str) -> None:
        """Initialize the object."""
        super(InvalidDirectiveErrorResponse, self).__init__(
            request_object, "INVALID_DIRECTIVE", message
        )


class InvalidValueErrorResponse(GenericErrorResponse):
    """Object represnting the requested value is not supported error."""

    def __init__(self, request_object: EndpointRequest, message: str) -> None:
        """Initialize the object."""
        super(InvalidValueErrorResponse, self).__init__(
            request_object, "INVALID_VALUE", message
        )


class BridgeUnreachableErrorResponse(GenericErrorResponse):
    """Object represnting the destination bridge is unreachable error."""

    def __init__(self, request_object: EndpointRequest, message: str) -> None:
        """Initialize the object."""
        super(BridgeUnreachableErrorResponse, self).__init__(
            request_object, "BRIDGE_UNREACHABLE", message
        )


class NoSuchEndpointErrorResponse(GenericErrorResponse):
    """Object represnting the requested endpoint doesn't exist error."""

    def __init__(self, request_object: EndpointRequest, message: str) -> None:
        """Initialize the object."""
        super(NoSuchEndpointErrorResponse, self).__init__(
            request_object, "NO_SUCH_ENDPOINT", message
        )


class InternalErrorResponse(GenericErrorResponse):
    """Object represnting the internal error."""

    def __init__(self, request_object: GenericRequest, message: str) -> None:
        """Initialize the object."""
        super(InternalErrorResponse, self).__init__(
            request_object, "INTERNAL_ERROR", message
        )
