from dataclasses import dataclass
import re
from enum import Enum

from typing import Literal

XAERO_WAYPOINT_REGEX = re.compile(
    r"waypoint:([A-Za-z\'\ ]+):([A-Z]):((-?\d+)|~:):((-?\d+)|~):((-?\d+)|~):([0-9]+):(true|false):([0-9]+):(\w+):(true|false):(\d+):(\d+):(true|false)"
)


class WaypointKind(Enum):
    NORMAL: int = 0
    DEATH: int = 1
    OLD_DEATH: int = 2
    DESTINATION: int = 3


class WaypointVisibility(Enum):
    LOCAL: int = 0
    GLOBAL: int = 1
    WORLD_MAP_LOCAL: int = 2
    WORLD_MAP_GLOBAL: int = 3


@dataclass
class Waypoint:
    name: str
    x: int
    z: int
    initials: str = "X"
    y: int | Literal["~"] = "~"
    color: int = 5
    disabled: bool = False
    wp_type: int | WaypointKind = 3
    wp_set: str = "ships"
    rotate_on_tp: bool = False
    tp_yaw: int = 0
    visibility_type: int | WaypointVisibility = 0
    destination: bool = False

    def __post_init__(self):
        if isinstance(self.wp_type, int):
            self.wp_type = WaypointKind(self.wp_type)

        if isinstance(self.visibility_type, int):
            self.visibility_type = WaypointKind(self.visibility_type)

    def __str__(self):
        return f"waypoint:{self.name}:{self.initials}:{self.x}:{self.y}:{self.z}:{self.color}:{str(self.disabled).lower()}:{self.wp_type.value}:{self.wp_set}:{str(self.rotate_on_tp).lower()}:{self.tp_yaw}:{self.visibility_type.value}:{str(self.destination).lower()}"
