"""WallPanel project automation classes for use with AppDaemon.

.. codeauthor:: Tomer Figenblat <tomer.figenblat@gmail.com>

"""
import json
from typing import Dict, Optional

import appdaemon.plugins.hass.hassapi as hass


class WallPanelsExtractAttributesFromMessage(hass.Hass):
    """Automation for extracting data from the wall panel app mqtt messages.

    The extracted data will be state attributes in HA entity.

    Example:
      .. code-block:: yaml

          nursery_panel_extract_attributes_for_battery:
            module: wallpanels_project
            class: WallPanelsExtractAttributesFromMessage
            sensor_entity: "sensor.wallpanel_nursery_battery"
            sensor_topic: "wallpanel/nursery_dash/sensor/battery"

    """

    def initialize(self) -> None:
        """Initialize the automation, and register the listenr."""
        self.entity = self.args["sensor_entity"]
        self.battery_handler = self.listen_event(
            self.mqtt_battery_message,
            "MQTT_MESSAGE",
            topic=self.args["sensor_topic"],
            namespace="mqtt",
        )

    def mqtt_battery_message(
        self, event_name: str, data: Dict, kwargs: Optional[Dict]
    ) -> None:
        """Use for handling mqtt message events.

        Origin payload example:
        {"value":47,"unit":"%","charging":false,"acPlugged":false,"usbPlugged":false}
        """
        payload_data = json.loads(data["payload"])

        entity_state = payload_data["value"]
        entity_attributes = self.get_state(self.entity, attribute="all")[
            "attributes"
        ]

        entity_attributes["charging"] = payload_data["charging"]
        entity_attributes["acPlugged"] = payload_data["acPlugged"]
        entity_attributes["usbPlugged"] = payload_data["usbPlugged"]

        self.set_state(
            self.entity, state=entity_state, attributes=entity_attributes
        )
