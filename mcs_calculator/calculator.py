"""Main MCS Heat Pump Calculator class."""
from typing import Dict, List, Optional
from dataclasses import dataclass
import math

from .room import Room, Building, Wall, Window, Floor
from .data_tables import DegreeDays, FloorUValues, RoomTemperatures, VentilationRates


@dataclass
class HeatPumpSpecs:
    """Heat pump specification."""
    model: str
    capacity_kw: float  # Rated capacity at design conditions
    cop: float  # Coefficient of Performance
    flow_temp: float = 45.0  # °C
    return_temp: float = 40.0  # °C


class HeatPumpCalculator:
    """MCS Heat Pump Calculator following BS EN 12831."""

    def __init__(self, postcode_area: str, building_category: str = 'B'):
        """
        Initialize calculator.

        Args:
            postcode_area: UK postcode area (e.g., 'SW', 'M', 'EH')
            building_category: 'A', 'B', or 'C' for ventilation rates
        """
        self.postcode_area = postcode_area.upper()
        self.building_category = building_category

        # Get degree days and design temp for location
        self.degree_days = DegreeDays.get_degree_days(self.postcode_area)
        self.design_external_temp = DegreeDays.get_design_temp(self.postcode_area)
        self.location = DegreeDays.get_location(self.postcode_area)

        if self.degree_days is None:
            raise ValueError(f"Unknown postcode area: {postcode_area}")

        self.building = None

    def create_building(self, name: str) -> Building:
        """Create a new building."""
        self.building = Building(name=name, postcode_area=self.postcode_area)
        return self.building

    def create_room(
        self,
        name: str,
        room_type: str,
        floor_area: float = 0.0,
        height: float = 2.4,
        design_temp: Optional[float] = None,
        air_change_rate: Optional[float] = None
    ) -> Room:
        """
        Create a room with default parameters.

        Args:
            name: Room name
            room_type: Room type (e.g., 'Lounge', 'Bedroom')
            floor_area: Floor area (m²)
            height: Room height (m)
            design_temp: Design temperature (°C), or None for default
            air_change_rate: Air change rate (ACH), or None for default

        Returns:
            Room object
        """
        if design_temp is None:
            design_temp = RoomTemperatures.get_temperature(room_type)

        if air_change_rate is None:
            air_change_rate = VentilationRates.get_rate(room_type, self.building_category)

        volume = floor_area * height

        return Room(
            name=name,
            room_type=room_type,
            design_temp=design_temp,
            volume=volume,
            air_change_rate=air_change_rate,
            height=height
        )

    def calculate_building_heat_loss(self) -> Dict:
        """Calculate heat loss for the entire building."""
        if not self.building:
            raise ValueError("No building created. Call create_building() first.")

        return self.building.get_summary(
            external_temp=self.design_external_temp,
            degree_days=self.degree_days
        )

    def calculate_hot_water_energy(
        self,
        num_occupants: int,
        daily_usage_litres: Optional[float] = None,
        cold_water_temp: float = 10.0,
        hot_water_temp: float = 60.0
    ) -> Dict[str, float]:
        """
        Calculate hot water energy requirement.

        Args:
            num_occupants: Number of occupants
            daily_usage_litres: Daily hot water usage (L), or None for default
            cold_water_temp: Cold water temperature (°C)
            hot_water_temp: Hot water storage temperature (°C)

        Returns:
            Dict with daily and annual energy requirements
        """
        # Default usage: 50 litres per person per day at 60°C
        if daily_usage_litres is None:
            daily_usage_litres = num_occupants * 50

        # Energy required (kWh/day) = Volume × ΔT × Specific Heat / 3600
        # Specific heat of water: 4.186 kJ/(kg·K) = 1.163 Wh/(L·K)
        temp_diff = hot_water_temp - cold_water_temp
        daily_energy_kwh = daily_usage_litres * temp_diff * 1.163 / 1000

        # Annual energy
        annual_energy_kwh = daily_energy_kwh * 365

        return {
            'daily_usage_litres': daily_usage_litres,
            'daily_energy_kwh': daily_energy_kwh,
            'annual_energy_kwh': annual_energy_kwh,
            'cold_water_temp': cold_water_temp,
            'hot_water_temp': hot_water_temp
        }

    def size_heat_pump(
        self,
        design_heat_loss_kw: float,
        hot_water_demand_kw: float = 0.0,
        oversizing_factor: float = 1.0
    ) -> Dict[str, float]:
        """
        Size heat pump based on heat loss and hot water demand.

        Args:
            design_heat_loss_kw: Design heat loss in kW
            hot_water_demand_kw: Hot water demand in kW (peak)
            oversizing_factor: Oversizing factor (typically 1.0-1.1)

        Returns:
            Dict with sizing information
        """
        # Total design capacity
        total_capacity = (design_heat_loss_kw + hot_water_demand_kw) * oversizing_factor

        return {
            'design_heat_loss_kw': design_heat_loss_kw,
            'hot_water_demand_kw': hot_water_demand_kw,
            'oversizing_factor': oversizing_factor,
            'required_capacity_kw': total_capacity
        }

    def calculate_annual_energy_consumption(
        self,
        space_heating_kwh: float,
        hot_water_kwh: float,
        cop: float
    ) -> Dict[str, float]:
        """
        Calculate annual energy consumption and costs.

        Args:
            space_heating_kwh: Annual space heating energy (kWh)
            hot_water_kwh: Annual hot water energy (kWh)
            cop: Heat pump Coefficient of Performance

        Returns:
            Dict with energy consumption breakdown
        """
        total_heat_demand = space_heating_kwh + hot_water_kwh
        electricity_consumption = total_heat_demand / cop

        return {
            'space_heating_demand_kwh': space_heating_kwh,
            'hot_water_demand_kwh': hot_water_kwh,
            'total_heat_demand_kwh': total_heat_demand,
            'cop': cop,
            'electricity_consumption_kwh': electricity_consumption,
            'efficiency_factor': cop
        }

    def calculate_radiator_sizing(
        self,
        room_heat_loss_w: float,
        room_temp: float,
        flow_temp: float = 45.0,
        return_temp: float = 40.0
    ) -> Dict[str, float]:
        """
        Calculate radiator sizing for low temperature heat pump system.

        Args:
            room_heat_loss_w: Room heat loss in Watts
            room_temp: Room design temperature (°C)
            flow_temp: Flow temperature (°C)
            return_temp: Return temperature (°C)

        Returns:
            Dict with radiator sizing information
        """
        # Mean water temperature
        mean_water_temp = (flow_temp + return_temp) / 2

        # Delta T (mean water temp - room temp)
        delta_t = mean_water_temp - room_temp

        # Standard radiators are rated at delta T = 50°C
        delta_t_50 = 50.0

        # Calculate required output at delta T 50
        # Output varies with (ΔT/50)^n where n ≈ 1.3 for radiators
        n = 1.3
        output_at_delta_50 = room_heat_loss_w / ((delta_t / delta_t_50) ** n)

        return {
            'room_heat_loss_w': room_heat_loss_w,
            'flow_temp': flow_temp,
            'return_temp': return_temp,
            'mean_water_temp': mean_water_temp,
            'delta_t': delta_t,
            'required_output_at_delta_t_50': output_at_delta_50,
            'sizing_factor': output_at_delta_50 / room_heat_loss_w
        }

    def get_location_info(self) -> Dict[str, any]:
        """Get location information."""
        return {
            'postcode_area': self.postcode_area,
            'location': self.location,
            'design_external_temp': self.design_external_temp,
            'degree_days': self.degree_days,
            'building_category': self.building_category
        }
