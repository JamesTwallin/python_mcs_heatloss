"""Room heat loss calculation module."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import math


@dataclass
class Wall:
    """Wall element for heat loss calculation."""
    name: str
    area: float  # m²
    u_value: float  # W/m²K
    temperature_factor: float = 1.0  # For unheated spaces
    boundary: str = 'external'  # 'external', 'ground', 'unheated', or room name
    boundary_temp: Optional[float] = None  # Temperature of boundary (for adjacent rooms)

    def heat_loss_watts(self, temp_diff: float) -> float:
        """Calculate heat loss through wall in Watts."""
        return self.area * self.u_value * temp_diff * self.temperature_factor

    def heat_loss_kwh(self, temp_diff: float, degree_days: float) -> float:
        """Calculate annual heat loss through wall in kWh."""
        # kWh = Watts × hours / 1000
        # Using degree days: kWh = U × A × DD × 24 / 1000
        return self.area * self.u_value * degree_days * 24 / 1000 * self.temperature_factor


@dataclass
class Window:
    """Window element for heat loss calculation."""
    name: str
    area: float  # m²
    u_value: float  # W/m²K

    def heat_loss_watts(self, temp_diff: float) -> float:
        """Calculate heat loss through window in Watts."""
        return self.area * self.u_value * temp_diff

    def heat_loss_kwh(self, temp_diff: float, degree_days: float) -> float:
        """Calculate annual heat loss through window in kWh."""
        return self.area * self.u_value * degree_days * 24 / 1000


@dataclass
class Floor:
    """Floor element for heat loss calculation."""
    name: str
    area: float  # m²
    u_value: float  # W/m²K
    temperature_factor: float = 0.5  # Ground floors typically 0.5

    def heat_loss_watts(self, temp_diff: float) -> float:
        """Calculate heat loss through floor in Watts."""
        return self.area * self.u_value * temp_diff * self.temperature_factor

    def heat_loss_kwh(self, temp_diff: float, degree_days: float) -> float:
        """Calculate annual heat loss through floor in kWh."""
        return self.area * self.u_value * degree_days * 24 / 1000 * self.temperature_factor


@dataclass
class Room:
    """Room heat loss calculation."""
    name: str
    room_type: str  # e.g., 'Lounge', 'Bedroom', etc.
    design_temp: float  # °C
    volume: float = 0.0  # m³
    air_change_rate: float = 1.0  # ACH (air changes per hour)

    walls: List[Wall] = field(default_factory=list)
    windows: List[Window] = field(default_factory=list)
    floors: List[Floor] = field(default_factory=list)

    # Additional heat losses
    thermal_bridging_factor: float = 0.0  # Typically 0.15 for post-2006
    height: float = 2.4  # m

    def __post_init__(self):
        """Initialize calculated fields."""
        if self.volume == 0 and self.floors:
            # Estimate volume from floor area and height
            total_floor_area = sum(f.area for f in self.floors)
            self.volume = total_floor_area * self.height

    def fabric_heat_loss_watts(self, external_temp: float, room_temps: Optional[Dict[str, float]] = None) -> Dict[str, float]:
        """
        Calculate fabric heat loss in Watts.

        Args:
            external_temp: External temperature
            room_temps: Dict mapping room names to temperatures (for inter-room heat transfer)

        Returns:
            Dict with 'walls', 'windows', 'floors', 'total', 'inter_room'
        """
        if room_temps is None:
            room_temps = {}

        wall_loss = 0
        inter_room_loss = 0

        for wall in self.walls:
            # Determine temperature difference based on boundary
            if wall.boundary == 'external':
                temp_diff = self.design_temp - external_temp
            elif wall.boundary == 'ground':
                # Use boundary_temp if set, otherwise use temp_factor approach
                ground_temp = wall.boundary_temp if wall.boundary_temp is not None else external_temp
                temp_diff = self.design_temp - ground_temp
            elif wall.boundary == 'unheated':
                # Unheated space - use boundary_temp if set
                unheated_temp = wall.boundary_temp if wall.boundary_temp is not None else 18
                temp_diff = self.design_temp - unheated_temp
            elif wall.boundary in room_temps:
                # Adjacent room - calculate inter-room heat transfer
                adjacent_temp = room_temps[wall.boundary]
                temp_diff = self.design_temp - adjacent_temp
                # Track inter-room transfers separately
                inter_room_loss += wall.heat_loss_watts(temp_diff)
                continue  # Don't add to wall_loss
            else:
                # Default to external
                temp_diff = self.design_temp - external_temp

            wall_loss += wall.heat_loss_watts(temp_diff)

        window_loss = sum(w.heat_loss_watts(self.design_temp - external_temp) for w in self.windows)
        floor_loss = sum(f.heat_loss_watts(self.design_temp - external_temp) for f in self.floors)

        total_fabric = wall_loss + window_loss + floor_loss + inter_room_loss

        # Add thermal bridging
        thermal_bridging = total_fabric * self.thermal_bridging_factor

        return {
            'walls': wall_loss,
            'windows': window_loss,
            'floors': floor_loss,
            'inter_room': inter_room_loss,
            'thermal_bridging': thermal_bridging,
            'total': total_fabric + thermal_bridging
        }

    def fabric_heat_loss_kwh(self, external_temp: float, degree_days: float) -> Dict[str, float]:
        """
        Calculate annual fabric heat loss in kWh.

        Returns:
            Dict with 'walls', 'windows', 'floors', 'total'
        """
        temp_diff = self.design_temp - external_temp

        wall_loss = sum(w.heat_loss_kwh(temp_diff, degree_days) for w in self.walls)
        window_loss = sum(w.heat_loss_kwh(temp_diff, degree_days) for w in self.windows)
        floor_loss = sum(f.heat_loss_kwh(temp_diff, degree_days) for f in self.floors)

        total_fabric = wall_loss + window_loss + floor_loss

        # Add thermal bridging
        thermal_bridging = total_fabric * self.thermal_bridging_factor

        return {
            'walls': wall_loss,
            'windows': window_loss,
            'floors': floor_loss,
            'thermal_bridging': thermal_bridging,
            'total': total_fabric + thermal_bridging
        }

    def ventilation_heat_loss_watts(self, external_temp: float) -> float:
        """
        Calculate ventilation heat loss in Watts.

        Uses: Q = 0.33 × n × V × ΔT
        where:
            0.33 = specific heat capacity of air (Wh/m³K)
            n = air change rate (ACH)
            V = volume (m³)
            ΔT = temperature difference (K)
        """
        temp_diff = self.design_temp - external_temp
        return 0.33 * self.air_change_rate * self.volume * temp_diff

    def ventilation_heat_loss_kwh(self, external_temp: float, degree_days: float) -> float:
        """
        Calculate annual ventilation heat loss in kWh.
        """
        # kWh = 0.33 × n × V × DD × 24 / 1000
        return 0.33 * self.air_change_rate * self.volume * degree_days * 24 / 1000

    def total_heat_loss_watts(self, external_temp: float, room_temps: Optional[Dict[str, float]] = None) -> float:
        """Calculate total heat loss (fabric + ventilation) in Watts."""
        fabric = self.fabric_heat_loss_watts(external_temp, room_temps)
        ventilation = self.ventilation_heat_loss_watts(external_temp)
        return fabric['total'] + ventilation

    def total_heat_loss_kwh(self, external_temp: float, degree_days: float) -> float:
        """Calculate annual total heat loss in kWh."""
        fabric = self.fabric_heat_loss_kwh(external_temp, degree_days)
        ventilation = self.ventilation_heat_loss_kwh(external_temp, degree_days)
        return fabric['total'] + ventilation

    def get_heat_loss_summary(self, external_temp: float, degree_days: float, room_temps: Optional[Dict[str, float]] = None) -> Dict:
        """Get complete heat loss summary."""
        fabric_watts = self.fabric_heat_loss_watts(external_temp, room_temps)
        fabric_kwh = self.fabric_heat_loss_kwh(external_temp, degree_days)
        vent_watts = self.ventilation_heat_loss_watts(external_temp)
        vent_kwh = self.ventilation_heat_loss_kwh(external_temp, degree_days)

        return {
            'room_name': self.name,
            'room_type': self.room_type,
            'design_temp': self.design_temp,
            'external_temp': external_temp,
            'volume': self.volume,
            'fabric_loss': {
                'watts': fabric_watts,
                'kwh': fabric_kwh
            },
            'ventilation_loss': {
                'watts': vent_watts,
                'kwh': vent_kwh
            },
            'total_loss': {
                'watts': fabric_watts['total'] + vent_watts,
                'kwh': fabric_kwh['total'] + vent_kwh
            }
        }


@dataclass
class Building:
    """Building containing multiple rooms."""
    name: str
    postcode_area: str
    rooms: List[Room] = field(default_factory=list)

    def add_room(self, room: Room):
        """Add a room to the building."""
        self.rooms.append(room)

    def _get_room_temps(self) -> Dict[str, float]:
        """Get mapping of room names to temperatures for inter-room heat transfer."""
        return {room.name.lower(): room.design_temp for room in self.rooms}

    def total_heat_loss_watts(self, external_temp: float, include_inter_room: bool = True) -> float:
        """
        Calculate total building heat loss in Watts.

        Args:
            external_temp: External temperature
            include_inter_room: If True, include inter-room heat transfer

        Returns:
            Total heat loss in Watts
        """
        if include_inter_room:
            room_temps = self._get_room_temps()
            return sum(room.total_heat_loss_watts(external_temp, room_temps) for room in self.rooms)
        else:
            return sum(room.total_heat_loss_watts(external_temp) for room in self.rooms)

    def total_heat_loss_kwh(self, external_temp: float, degree_days: float) -> float:
        """Calculate total building annual heat loss in kWh."""
        return sum(room.total_heat_loss_kwh(external_temp, degree_days) for room in self.rooms)

    def get_summary(self, external_temp: float, degree_days: float, include_inter_room: bool = True) -> Dict:
        """
        Get complete building heat loss summary.

        Args:
            external_temp: External temperature
            degree_days: Degree days for location
            include_inter_room: If True, include inter-room heat transfer
        """
        room_temps = self._get_room_temps() if include_inter_room else {}

        room_summaries = [
            room.get_heat_loss_summary(external_temp, degree_days, room_temps)
            for room in self.rooms
        ]

        total_watts = sum(r['total_loss']['watts'] for r in room_summaries)
        total_kwh = sum(r['total_loss']['kwh'] for r in room_summaries)

        return {
            'building_name': self.name,
            'postcode_area': self.postcode_area,
            'external_temp': external_temp,
            'degree_days': degree_days,
            'num_rooms': len(self.rooms),
            'rooms': room_summaries,
            'total_heat_loss': {
                'watts': total_watts,
                'kwh': total_kwh
            },
            'inter_room_enabled': include_inter_room
        }
