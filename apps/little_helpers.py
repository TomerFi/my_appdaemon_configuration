"""Global module for use with AppDaemon, Helper functions.

.. codeauthor:: Tomer Figenblat <tomer.figenblat@gmail.com>

"""
from datetime import datetime, timezone
from uuid import uuid4

import pytz

true_strings = [
    "True",
    "true",
    "Online",
    "online",
    "ON",
    "On",
    "on",
    "Open",
    "open",
    "Motion Detected",
    "motion_detected",
]

false_strings = [
    "False",
    "false",
    "Offline",
    "offline",
    "OFF",
    "Off",
    "off",
    "Closed",
    "closed",
    "No Motion",
    "no_motion",
]


def get_elapsed_in_milliseconds(from_datetime: str) -> int:
    """Use for calculating time diffrence in milliseconds.

    From the time passed as datetime string argument until now.
    """
    fixed_from = (
        from_datetime.rsplit(":", 1)[0] + from_datetime.rsplit(":", 1)[1]
    )
    return int(
        (
            datetime.now(pytz.utc)
            - datetime.strptime(fixed_from, "%Y-%m-%dT%H:%M:%S.%f%z")
        ).total_seconds()
        * 1000
    )


def get_uuid_str() -> str:
    """Use for creating unique identifier v4 (32 hex digits + 4 dashes)."""
    return str(uuid4())


def get_iso_datetime_utc_tz_str():
    """Use for creting a string time object timezone'd in iso format."""
    return str(datetime.utcnow().replace(tzinfo=timezone.utc).isoformat())


def entityId_to_endpointId(entityId: str) -> str:
    """Use for converting HA entity id to Alexa endpoint."""
    return entityId.replace(".", "_", 1)


def endpointId_to_entityId(endpointId: str) -> str:
    """Use for converting Alexa endpoint to HA entity id."""
    return endpointId.replace("_", ".", 1)
