"""Automation classes for use with AppDaemon, Various automations.

.. codeauthor:: Tomer Figenblat <tomer.figenblat@gmail.com>

"""
from typing import Dict, List, Optional

import appdaemon.plugins.hass.hassapi as hass
import little_helpers


class BatteryLowSendNotification(hass.Hass):
    """Automation for sending notification.

    When the battery percent of the requested device has dropped below
    the configured threshold.

    Example:
      .. code-block:: yaml

          nursery_panel_low_battery_notification:
            module: automations
            class: BatteryLowSendNotification
            sensor_entity: 'sensor.wallpanel_nursery_battery'
            notify_service: 'notify.telegram_tomer_service'
            threshold_precent: 20
            device_name: "Nursery Tablet"

    """

    def initialize(self) -> None:
        """Initialize the automation, and register the listenr."""
        self.entity = self.args["sensor_entity"]
        self.notify_service = self.args["notify_service"].replace(
            "notify.", "notify/"
        )
        self.threshold_precent = int(self.args["threshold_precent"])
        self.device_name = self.args["device_name"]
        self.state_handler = self.listen_state(
            self.battery_state_changed, self.entity
        )

    def battery_state_changed(
        self,
        entity: Optional[str],
        attribute: Optional[str],
        old: str,
        new: str,
        kwargs: Optional[Dict],
    ) -> None:
        """Use for handling state change events."""
        if (
            int(new) <= self.threshold_precent
            and int(old) > self.threshold_precent
        ):
            self.call_service(
                self.notify_service,
                title="Battery Low",
                message=(
                    "Battery percent on {} has dropped below the {}"
                    "threshold, please charge the device."
                ).format(self.device_name, str(self.threshold_precent)),
            )


class SensorsControlSwitches(hass.Hass):
    """Automation for turning switches on or off Based on sensor state.

    Example:
      .. code-block:: yaml

          closet_room_door_control_switch:
            module: automations
            class: SensorsControlSwitches
            sensor_entity: 'sensor.broadlink_s1c_closet_room'
            switch_entities:
              - 'switch.closet_room_light'
              - 'switch.shower_light'
            turn_on_closed_to_open: true
            turn_off_open_to_closed: false
            global_dependencies: little_helpers

    """

    def initialize(self) -> None:
        """Initialize the automation, and register the listenr."""
        self.sensor_entity = self.args["sensor_entity"]
        self.switch_entities = []  # type: List[str]
        if isinstance(self.args["switch_entities"], str):
            self.switch_entities.append(self.args["switch_entities"])
        else:
            for switch in self.args["switch_entities"]:
                self.switch_entities.append(switch)
        self.turn_on_closed_to_open = self.args["turn_on_closed_to_open"]
        self.turn_off_open_to_closed = self.args["turn_off_open_to_closed"]
        self.state_handler = self.listen_state(
            self.state_changes, self.sensor_entity
        )

    def state_changes(
        self,
        entity: Optional[str],
        attribute: Optional[str],
        old: str,
        new: str,
        kwargs: Optional[Dict],
    ) -> None:
        """Use for handling state change events."""
        if (
            self.turn_on_closed_to_open
            and str(old) in little_helpers.false_strings
            and str(new) in little_helpers.true_strings
        ):
            for switch in self.switch_entities:
                self.call_service("switch/turn_on", entity_id=switch)
        elif (
            self.turn_off_open_to_closed
            and str(old) in little_helpers.true_strings
            and str(new) in little_helpers.false_strings
        ):
            for switch in self.switch_entities:
                self.call_service("switch/turn_off", entity_id=switch)


class CallServiceOnMqttMessage(hass.Hass):
    """Automation for calling a service and pass data on incoming mqtt message.

    Example:
      .. code-block:: yaml

          bedroom_sticker_switch_toggle:
            module: automations
            class: CallServiceOnMqttMessage
            topic: 'omg/rfgw_hallway/433toMQTT'
            payload: '9127250'
            service: 'switch.toggle'
            data:
              entity_id: "switch.bedroom_main_light"

    """

    def initialize(self) -> None:
        """Initialize the automation, and register the listenr."""
        self.service = self.args["service"].replace(".", "/")
        self.data = self.args["data"]
        self.message_handler = self.listen_event(
            self.message_arrived,
            "MQTT_MESSAGE",
            topic=self.args["topic"],
            payload=self.args["payload"],
            namespace="mqtt",
        )

    def message_arrived(
        self, event_name: str, data: Optional[Dict], kwargs: Optional[Dict]
    ) -> None:
        """Use for handling mqtt message events."""
        self.call_service(self.service, **self.data)
