"""Global module for use with AppDaemon, Alexa Request Objects.

.. codeauthor:: Tomer Figenblat <tomer.figenblat@gmail.com>

"""
from typing import Dict


class GenericRequest:
    """Object represnting the generic request.

    Do not use directly (unless on errors),
    either use the EndpointRequest subclass for request invloving endpoint data
    or the DiscoveryRequest subclass for discovery requests.

    Do not use error responses for discovery requests,
    either return a success request with no endpoints data or do not return
    anything.
    """

    def __init__(
        self, request: Dict, init_namespace: str, init_name: str
    ) -> None:
        """Initialize the object."""
        self._rawRequest = request
        self._namespace = init_namespace
        self._name = init_name
        self._payloadVersion = request["directive"]["header"]["payloadVersion"]
        self._messageId = request["directive"]["header"]["messageId"]

    @property
    def rawRequest(self) -> Dict:
        """str: Return the origin request."""
        return self._rawRequest

    @property
    def namespace(self) -> str:
        """str: Return the namespace."""
        return self._namespace

    @property
    def name(self) -> str:
        """str: Return the name."""
        return self._name

    @property
    def payloadVersion(self) -> str:
        """str: Return the payload version."""
        return self._payloadVersion

    @property
    def messageId(self) -> str:
        """str: Return the message id."""
        return self._messageId


class EndpointRequest(GenericRequest):
    """Object represnting requests containing endpoint data.

    Use directly for report state requests only!
    for other types of requests use any of the folowwing subclassess.
    """

    def __init__(
        self, request: Dict, init_namespace: str, init_name: str
    ) -> None:
        """Initialize the object."""
        super(EndpointRequest, self).__init__(
            request, init_namespace, init_name
        )
        self._correlationToken = request["directive"]["header"][
            "correlationToken"
        ]
        self._endpointId = request["directive"]["endpoint"]["endpointId"]
        self._tokenType = request["directive"]["endpoint"]["scope"]["type"]
        self._token = request["directive"]["endpoint"]["scope"]["token"]

    @property
    def correlationToken(self) -> str:
        """str: Return the correlation token."""
        return self._correlationToken

    @property
    def endpointId(self) -> str:
        """str: Return the endpoint id."""
        return self._endpointId

    @property
    def tokenType(self) -> str:
        """str: Return the token type."""
        return self._tokenType

    @property
    def token(self) -> str:
        """str: Return the token value."""
        return self._token


class DiscoveryRequest(GenericRequest):
    """Object represnting discovery requests."""

    def __init__(
        self, request: Dict, init_namespace: str, init_name: str
    ) -> None:
        """Initialize the object."""
        super(DiscoveryRequest, self).__init__(
            request, init_namespace, init_name
        )
        self._tokenType = request["directive"]["payload"]["scope"]["type"]
        self._token = request["directive"]["payload"]["scope"]["token"]

    @property
    def tokenType(self) -> str:
        """str: Return the token type."""
        return self._tokenType

    @property
    def token(self) -> str:
        """str: Return the token value."""
        return self._token


class AdjustThermostatTemperatureRequest(EndpointRequest):
    """Object represnting the adjust tempereture by delta request."""

    def __init__(
        self, request: Dict, init_namespace: str, init_name: str
    ) -> None:
        """Initialize the object."""
        super(AdjustThermostatTemperatureRequest, self).__init__(
            request, init_namespace, init_name
        )
        self._value = request["directive"]["payload"]["targetSetpointDelta"][
            "value"
        ]
        self._scale = request["directive"]["payload"]["targetSetpointDelta"][
            "scale"
        ]

    @property
    def value(self) -> str:
        """str: Return the tempereture value."""
        return self._value

    @property
    def scale(self) -> str:
        """str: Return the tempereture scale."""
        return self._scale


class SetThermostatTemperatureRequest(EndpointRequest):
    """Object represnting the set the tempereture to x request."""

    def __init__(
        self, request: Dict, init_namespace: str, init_name: str
    ) -> None:
        """Initialize the object."""
        super(SetThermostatTemperatureRequest, self).__init__(
            request, init_namespace, init_name
        )
        self._value = request["directive"]["payload"]["targetSetpoint"][
            "value"
        ]
        self._scale = request["directive"]["payload"]["targetSetpoint"][
            "scale"
        ]

    @property
    def value(self) -> str:
        """str: Return the tempereture value."""
        return self._value

    @property
    def scale(self) -> str:
        """str: Return the tempereture scale."""
        return self._scale


class SetThermostatModeRequest(EndpointRequest):
    """Object represnting the set the mode to to x request."""

    def __init__(
        self, request: Dict, init_namespace: str, init_name: str
    ) -> None:
        """Initialize the object."""
        super(SetThermostatModeRequest, self).__init__(
            request, init_namespace, init_name
        )
        self._value = request["directive"]["payload"]["thermostatMode"][
            "value"
        ]

    @property
    def value(self) -> str:
        """str: Return the tempereture value."""
        return self._value


class PowerControlRequest(EndpointRequest):
    """Object represnting the set the mode to to x request."""

    def __init__(
        self, request: Dict, init_namespace: str, init_name: str
    ) -> None:
        """Initialize the object."""
        super(PowerControlRequest, self).__init__(
            request, init_namespace, init_name
        )
        self._powerState = True if self.name == "TurnOn" else False

    @property
    def powerState(self) -> bool:
        """str: Return True of TurnOn power state."""
        return self._powerState
