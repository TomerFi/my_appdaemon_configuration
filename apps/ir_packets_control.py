"""Automation classes for use with AppDaemon, Climate and Fan Mqtt automations.

.. codeauthor:: Tomer Figenblat <tomer.figenblat@gmail.com>

"""
from typing import Dict, Optional

import appdaemon.plugins.hass.hassapi as hass
import ir_packets_manager
import little_helpers


class HandleMqttFan(hass.Hass):
    """Automation for converting and sending Fan MQTT messages as ir packets.

    Example:
      .. code-block:: yaml

          nursery_ceiling_fan_off:
            module: ir_packets_control
            class: HandleMqttFan
            topic: 'tomerfi_custom_fan/nursery/command'
            payload: 'off'
            ir_transmitter_ip: "192.168.0.170"
            fan_type: "hyundai_ceiling_fan"
            command: 'off'
            global_dependencies: ir_packets_manager

    """

    def initialize(self) -> None:
        """Initialize the automation, and register the listenr."""
        self.ir_transmitter_ip = self.args["ir_transmitter_ip"]
        self.fan_type = self.args["fan_type"]
        self.command = self.args["command"]

        if self.args["payload"]:
            self.fan_handler = self.listen_event(
                self.message_arrived,
                "MQTT_MESSAGE",
                topic=self.args["topic"],
                payload=self.args["payload"],
                namespace="mqtt",
            )
        else:
            self.fan_handler = self.listen_event(
                self.message_arrived,
                "MQTT_MESSAGE",
                topic=self.args["topic"],
                namespace="mqtt",
            )

    def terminate(self) -> None:
        """Cancel listener on termination."""
        self.cancel_listen_event(self.fan_handler)

    def message_arrived(
        self, event_name: str, data: Optional[Dict], kwargs: Optional[Dict]
    ) -> None:
        """Use for handling mqtt message events."""
        self.call_service(
            "broadlink/send",
            host=self.ir_transmitter_ip,
            packet=ir_packets_manager.get_fan_packet(
                self.fan_type, self.command
            ),
        )


class HandleMqttACUnit(hass.Hass):
    """Automation for converting and sending AC MQTT messages as ir packets.

    Example:
      .. code-block:: yaml

          nursery_ac_automation:
            module: ir_packets_control
            class: HandleMqttACUnit
            climate_entity: climate.nursery_air_conditioner
            ir_transmitter_ip: "192.168.0.170"
            ac_type: "elco_small"
            default_mode_for_on: "cool"
            mode_command_topic: "tomerfi_custom_ac/nursery/mode"
            temperature_command_topic: "tomerfi_custom_ac/nursery/temperature"
            fan_mode_command_topic: "tomerfi_custom_ac/nursery/fan"

    """

    def initialize(self) -> None:
        """Initialize the automation, and register the listenr."""
        self.climate_entity = self.args["climate_entity"]
        self.default_mode_for_on = self.args["default_mode_for_on"]
        self.ir_transmitter_ip = self.args["ir_transmitter_ip"]
        self.ac_type = self.args["ac_type"]
        self.mode_command_topic = self.args["mode_command_topic"]
        self.temperature_command_topic = self.args["temperature_command_topic"]
        self.fan_mode_command_topic = self.args["fan_mode_command_topic"]

        self.mode_command_handler = self.listen_event(
            self.on_mode_command,
            "MQTT_MESSAGE",
            topic=self.mode_command_topic,
            namespace="mqtt",
        )
        self.temperature_command_handler = self.listen_event(
            self.on_temperature_command,
            "MQTT_MESSAGE",
            topic=self.temperature_command_topic,
            namespace="mqtt",
        )
        self.fan_mode_command_handler = self.listen_event(
            self.on_fan_mode_command,
            "MQTT_MESSAGE",
            topic=self.fan_mode_command_topic,
            namespace="mqtt",
        )

    def terminate(self) -> None:
        """Cancel listeners on termination."""
        self.cancel_listen_event(self.mode_command_handler)
        self.cancel_listen_event(self.temperature_command_handler)
        self.cancel_listen_event(self.fan_mode_command_handler)

    def on_mode_command(
        self, event_name: str, data: Dict, kwargs: Optional[Dict]
    ) -> None:
        """Use for handling mqtt message events for ac mode changes."""
        if data["payload"] in little_helpers.false_strings:
            packet = ir_packets_manager.get_ac_packet(
                self.ac_type, data["off"]
            )

        else:
            entity_data = self.get_state(self.climate_entity, attribute="all")
            packet = ir_packets_manager.get_ac_packet(
                self.ac_type,
                data["payload"],
                entity_data["attributes"]["fan_mode"],
                entity_data["attributes"]["temperature"],
            )

        self._send_packet(packet)

    def on_temperature_command(
        self, event_name: str, data: Dict, kwargs: Optional[Dict]
    ) -> None:
        """Use for handling mqtt message events for ac temperature changes."""
        entity_data = self.get_state(self.climate_entity, attribute="all")
        self._send_packet(
            ir_packets_manager.get_ac_packet(
                self.ac_type,
                entity_data["state"],
                entity_data["attributes"]["fan_mode"],
                float(data["payload"]),
            )
        )

    def on_fan_mode_command(
        self, event_name: str, data: Dict, kwargs: Optional[Dict]
    ) -> None:
        """Use for handling mqtt message events for ac fan changes."""
        entity_data = self.get_state(self.climate_entity, attribute="all")
        self._send_packet(
            ir_packets_manager.get_ac_packet(
                self.ac_type,
                entity_data["state"],
                data["payload"],
                entity_data["attributes"]["temperature"],
            )
        )

    def _send_packet(self, packet: str) -> None:
        """Use as helper function to send ir packets with broadlink."""
        self.call_service(
            "broadlink/send", host=self.ir_transmitter_ip, packet=packet
        )


class TemperatureSensorToMqtt(hass.Hass):
    """Automation for publishing sensor state changes as mqtt messages.

    Example:
      .. code-block:: yaml

          nursery_temperature_sensor_to_mqtt:
            module: ir_packets_control
            class: TemperatureSensorToMqtt
            sensor_entity: sensor.nursery_broadlink_a1_temperature
            topic: "tomerfi_custom_ac/nursery/current_temperature"

    """

    def initialize(self) -> None:
        """Initialize the automation, and register the listenr."""
        self.sensor_entity = self.args["sensor_entity"]
        self.topic = self.args["topic"]

        self.state_handler = self.listen_state(
            self.state_changed, entity=self.sensor_entity
        )

    def terminate(self) -> None:
        """Cancel listener on termination."""
        self.cancel_listen_state(self.state_handler)

    def state_changed(
        self,
        entity: Optional[str],
        attribute: Optional[str],
        old: str,
        new: str,
        kwargs: Optional[Dict],
    ) -> None:
        """Use for handling state change events."""
        self.call_service(
            "mqtt/publish", **{"topic": self.topic, "payload": new}
        )
