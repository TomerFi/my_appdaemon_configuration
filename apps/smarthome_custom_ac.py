"""AppDaemon application, Home Assistant Climate to Alexa Smart Thermostat.

Note:
  Access uri: https://<your_ha_ip_or_name>/api/appdaemon/AlexaCustomAC

  Legacy password is requierd for appdaemon,
  Please add '?api_password=YourSecretPassword' to the uri.

.. codeauthor:: Tomer Figenblat <tomer.figenblat@gmail.com>

"""
from typing import Any, Dict, Optional, Tuple

import alexa_request
import alexa_response_error
import alexa_response_success
import appdaemon.plugins.hass.hassapi as hassapi
import little_helpers


class AlexaCustomAC(hassapi.Hass):
    """AlexaCustomAC AppDaemon application.

    Bridging Home Assistant climate entities
    as smart thermostats for Alexa usage.
    """

    def initialize(self) -> None:
        """Initialize the application.

        Collect the arguments and register the endpoint.
        """
        self.entities = self.args["entities"]
        self.default_mode_for_on = self.args["default_mode_for_on"]
        self.scale = self.args["scale"] if "scale" in self.args else "CELSIUS"

        self.handler = self.register_endpoint(self.api_call, "AlexaCustomAC")

    def terminate(self) -> None:
        """Unregister the endpoint on termination."""
        self.unregister_endpoint(self.handler)

    def _handle_namespace_alexa(
        self, request: Dict, init_namespace: str, init_name: str
    ) -> Dict:
        """Handle calls with the Alexa namespace.

        Args:
          request: Dictionary reprensting the original request.
          init_namespace: The initial namespace of the request.
          init_name: The initial name of the request.

        Returns:
          Dict: a dictionary representation of the response.
          int: the http response code.

        Raises:
          Exception: When failed to construct a response.

        """
        try:
            if init_name == "ReportState":
                endpoint_request_object = alexa_request.EndpointRequest(
                    request, init_namespace, init_name
                )
                entity_id = little_helpers.endpointId_to_entityId(
                    endpoint_request_object.endpointId
                )
                entity_state = self.get_state(entity_id, attribute="all")
                success_response_object = alexa_response_success.StateReportResponse(  # noqa: E501
                    endpoint_request_object, entity_state, self.scale
                )
                response = success_response_object.create_response()
            else:
                generic_request_object = alexa_request.GenericRequest(
                    request, init_namespace, init_name
                )
                msg_literal = "name {} is unknown for namespace {}.".format(
                    init_name, init_namespace
                )
                invalid_response_object = alexa_response_error.InvalidDirectiveErrorResponse(  # noqa: E501
                    generic_request_object, msg_literal
                )
                response = invalid_response_object.create_response()
            return response
        except Exception as ex:
            raise Exception("ReportState directive failed.") from ex

    def _handle_namespace_alexa_discovery(
        self, request: Dict, init_namespace: str, init_name: str
    ) -> Optional[Dict]:
        """Handle calls with the Alexa.Discovery namespace.

        Args:
          request: Dictionary reprensting the original request.
          init_namespace: The initial namespace of the request.
          init_name: The initial name of the request.

        Returns:
          Dict: a dictionary representation of the response.
          int: the http response code.

        Raises:
          Exception: When failed to construct a response.

        Note:
          Do not use error responses for discovery requests,
          either return a success request with no endpoints data
          or do not return anything!

        """
        try:
            if init_name == "Discover":
                request_object = alexa_request.DiscoveryRequest(
                    request, init_namespace, init_name
                )
                endpoints_list = [
                    self.get_state(entity, attribute="all")
                    for entity in self.entities
                ]
                response_object = alexa_response_success.DiscoveryResponse(
                    request_object, endpoints_list
                )
                return response_object.create_response()
            else:
                return None
        except Exception as ex:
            raise Exception("Discovery directive failed.") from ex

    def _handle_namespace_alexa_power_controller(
        self, request: Dict, init_namespace: str, init_name: str
    ) -> Dict:
        """Handle calls with the Alexa.PowerController namespace.

        Args:
          request: Dictionary reprensting the original request.
          init_namespace: The initial namespace of the request.
          init_name: The initial name of the request.

        Returns:
          Dict: a dictionary representation of the response.
          int: the http response code.

        Raises:
          Exception: When failed to construct a response.

        """
        try:
            if init_name == "TurnOn" or init_name == "TurnOff":
                request_object = alexa_request.PowerControlRequest(
                    request, init_namespace, init_name
                )
                entity_id = little_helpers.endpointId_to_entityId(
                    request_object.endpointId
                )
                if entity_id in self.entities:
                    self.call_service(
                        "climate/set_operation_mode",
                        entity_id=entity_id,
                        operation_mode=(
                            self.default_mode_for_on
                            if init_name == "TurnOn"
                            else "off"
                        ),
                    )
                    entity_state = self.get_state(entity_id, attribute="all")
                    success_response_object = alexa_response_success.PowerControlResponse(  # noqa: E501
                        request_object, entity_state
                    )
                    response = success_response_object.create_response()
                else:
                    msg_literal = "unknown endpoint {}".format(
                        self.request_object.endpointId
                    )
                    no_endpoint_response_object = alexa_response_error.NoSuchEndpointErrorResponse(  # noqa: E501
                        request_object, msg_literal
                    )
                    response = no_endpoint_response_object.create_response()
            else:
                generic_request_object = alexa_request.GenericRequest(
                    request, init_namespace, init_name
                )
                msg_literal = "name {} is unknown for namespace {}.".format(
                    init_name, init_namespace
                )
                invalid_response_object = alexa_response_error.InvalidDirectiveErrorResponse(  # noqa: E501
                    generic_request_object, msg_literal
                )
                response = invalid_response_object.create_response()
            return response
        except Exception as ex:
            raise Exception("PowerControl directive failed.") from ex

    def _handle_namespace_alexa_thermostat_controller(
        self, request: Dict, init_namespace: str, init_name: str
    ) -> Dict:
        """Handle calls with the Alexa.ThermostatController namespace.

        Args:
          request: Dictionary reprensting the original request.
          init_namespace: The initial namespace of the request.
          init_name: The initial name of the request.

        Returns:
          Dict: a dictionary representation of the response.
          int: the http response code.

        Raises:
          Exception: When failed to construct a response.

        """
        try:
            if init_name == "SetTargetTemperature":
                request_object = alexa_request.SetThermostatTemperatureRequest(
                    request, init_namespace, init_name
                )  # type: Any
                entity_id = little_helpers.endpointId_to_entityId(
                    request_object.endpointId
                )
                entity_state = self.get_state(entity_id, attribute="all")
                if entity_state["state"].lower() == "off":
                    response_object = alexa_response_error.ThermostatIsOffErrorResponse(  # noqa: E501
                        request_object, "endpoint is off"
                    )
                    return response_object.create_response()

                targetTemp = round(float(request_object.value), 1)
                if (
                    targetTemp < entity_state["attributes"]["min_temp"]
                    or targetTemp > entity_state["attributes"]["max_temp"]
                ):
                    min_temp = str(entity_state["attributes"]["min_temp"])
                    max_temp = str(entity_state["attributes"]["max_temp"])
                    out_of_range_response_object = alexa_response_error.TemperatureOutOfRangeErrorResponse(  # noqa: E501
                        request_object,
                        "out of range",
                        min_temp,
                        max_temp,
                        self.scale,
                    )
                    return out_of_range_response_object.create_response()

                service_name = "climate/set_temperature"
                kwargs = {
                    "entity_id": entity_state["entity_id"],
                    "temperature": targetTemp,
                }

                entity_state["attributes"]["temperature"] = targetTemp

            elif init_name == "AdjustTargetTemperature":
                request_object = alexa_request.AdjustThermostatTemperatureRequest(  # noqa: E501
                    request, init_namespace, init_name
                )
                entity_id = little_helpers.endpointId_to_entityId(
                    request_object.endpointId
                )
                entity_state = self.get_state(entity_id, attribute="all")
                if entity_state["state"].lower() == "off":
                    response_object = alexa_response_error.ThermostatIsOffErrorResponse(  # noqa: E501
                        request_object, "endpoint is off"
                    )
                    return response_object.create_response()

                targetTemp = entity_state["attributes"]["temperature"] + (
                    round(float(request_object.value), 1)
                )
                if (
                    targetTemp < entity_state["attributes"]["min_temp"]
                    or targetTemp > entity_state["attributes"]["max_temp"]
                ):
                    min_temp = str(entity_state["attributes"]["min_temp"])
                    max_temp = str(entity_state["attributes"]["max_temp"])
                    out_of_range_response_object = alexa_response_error.TemperatureOutOfRangeErrorResponse(  # noqa: E501
                        request_object,
                        "out of range",
                        min_temp,
                        max_temp,
                        self.scale,
                    )
                    return out_of_range_response_object.create_response()

                service_name = "climate/set_temperature"
                kwargs = {
                    "entity_id": entity_state["entity_id"],
                    "temperature": targetTemp,
                }

                entity_state["attributes"]["temperature"] = targetTemp

            elif init_name == "SetThermostatMode":
                mode_request_object = alexa_request.SetThermostatModeRequest(
                    request, init_namespace, init_name
                )
                entity_id = little_helpers.endpointId_to_entityId(
                    mode_request_object.endpointId
                )
                entity_state = self.get_state(entity_id, attribute="all")

                service_name = "climate/set_operation_mode"
                kwargs = {
                    "entity_id": entity_state["entity_id"],
                    "operation_mode": mode_request_object.value.lower(),
                }

                entity_state["state"] = mode_request_object.value.lower()

            else:
                generic_request_object = alexa_request.GenericRequest(
                    request, init_namespace, init_name
                )
                msg_literal = "name {} is unknown for namespace {}.".format(
                    init_name, init_namespace
                )
                invalid_response_object = alexa_response_error.InvalidDirectiveErrorResponse(  # noqa: E501
                    generic_request_object, msg_literal
                )
                return invalid_response_object.create_response()

            self.call_service(service_name, **kwargs)
            success_response_object = alexa_response_success.ThermostatControlResponse(  # noqa: E501
                request_object, entity_state, self.scale
            )
            return success_response_object.create_response()

        except Exception as ex:
            raise Exception("ThermostatController directive failed.") from ex

    def api_call(self, request: Dict) -> Tuple[Optional[Dict], int]:
        """Handle all api calls.

        Returns:
          Dict: a dictionary representation of the response.
          int: the http response code.

        Raises:
          Exception: When failed to construct a response.

        """
        init_namespace = request["directive"]["header"]["namespace"]
        init_name = request["directive"]["header"]["name"]
        directive_to_handler = {
            "Alexa": self._handle_namespace_alexa,
            "Alexa.Discovery": self._handle_namespace_alexa_discovery,
            "Alexa.PowerController": (
                self._handle_namespace_alexa_power_controller
            ),
            "Alexa.ThermostatController": (
                self._handle_namespace_alexa_thermostat_controller
            ),
        }
        try:
            if init_namespace in directive_to_handler:
                response_dict = directive_to_handler[init_namespace](
                    request, init_namespace, init_name
                )
            else:
                request_object = alexa_request.GenericRequest(
                    request, init_namespace, init_name
                )
                msg_literal = "namespace {} is unknown.".format(init_namespace)
                response_object = alexa_response_error.InvalidDirectiveErrorResponse(  # noqa: E501
                    request_object, msg_literal
                )
                response_dict = response_object.create_response()
            return response_dict, 200
        except Exception as ex:
            request_object = alexa_request.GenericRequest(
                request, init_namespace, init_name
            )
            error_response_object = alexa_response_error.InternalErrorResponse(
                request_object, str(ex)
            )
            return error_response_object.create_response(), 200
