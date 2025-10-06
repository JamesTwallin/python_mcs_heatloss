"""Tests for MCS Heat Pump Calculator."""
import pytest
from mcs_calculator import HeatPumpCalculator, Room, Wall, Window, Floor
from mcs_calculator.data_tables import DegreeDays, FloorUValues, RoomTemperatures


class TestDegreeDays:
    """Test degree days lookup."""

    def test_known_postcode_areas(self):
        """Test known postcode areas return correct data."""
        assert DegreeDays.get_degree_days('SW') == 2033
        assert DegreeDays.get_degree_days('M') == 2275
        assert DegreeDays.get_degree_days('EH') == 2332

    def test_design_temperatures(self):
        """Test design external temperatures."""
        assert DegreeDays.get_design_temp('SW') == -2.0
        assert DegreeDays.get_design_temp('M') == -3.1
        assert DegreeDays.get_design_temp('AB') == -4.2

    def test_unknown_postcode(self):
        """Test unknown postcode returns None."""
        assert DegreeDays.get_degree_days('XX') is None
        assert DegreeDays.get_design_temp('YY') is None


class TestFloorUValues:
    """Test floor U-value calculations."""

    def test_solid_floor_calculation(self):
        """Test solid floor U-value calculation."""
        # Simple test case
        u_value = FloorUValues.calculate_floor_u_value(
            floor_type='solid',
            perimeter=20,
            area=25,
            wall_thickness=0.3,
            insulation_thickness=0.1
        )
        assert u_value > 0
        assert u_value < 1.0  # Reasonable range for insulated floor

    def test_suspended_floor_calculation(self):
        """Test suspended floor U-value calculation."""
        u_value = FloorUValues.calculate_floor_u_value(
            floor_type='suspended',
            perimeter=20,
            area=25,
            wall_thickness=0.3,
            insulation_thickness=0.1
        )
        assert u_value > 0
        assert u_value < 1.0


class TestRoomTemperatures:
    """Test room temperature defaults."""

    def test_standard_room_temps(self):
        """Test standard room temperatures."""
        assert RoomTemperatures.get_temperature('Lounge') == 21
        assert RoomTemperatures.get_temperature('Bedroom') == 18
        assert RoomTemperatures.get_temperature('Bathroom') == 22


class TestRoom:
    """Test room heat loss calculations."""

    def test_simple_room_fabric_loss(self):
        """Test basic fabric heat loss calculation."""
        room = Room(
            name='Test Room',
            room_type='Lounge',
            design_temp=21,
            volume=30,  # 5m x 6m x 2.4m
        )

        # Add a simple wall
        room.walls.append(Wall(
            name='External Wall',
            area=12,  # 5m x 2.4m
            u_value=0.3
        ))

        # Calculate heat loss at -2°C external
        external_temp = -2
        fabric_loss = room.fabric_heat_loss_watts(external_temp)

        # Expected: 12m² × 0.3 W/m²K × (21-(-2))K = 82.8W
        expected = 12 * 0.3 * (21 - (-2))
        assert abs(fabric_loss['walls'] - expected) < 0.1

    def test_ventilation_heat_loss(self):
        """Test ventilation heat loss calculation."""
        room = Room(
            name='Test Room',
            room_type='Lounge',
            design_temp=21,
            volume=30,
            air_change_rate=1.5
        )

        external_temp = -2
        vent_loss = room.ventilation_heat_loss_watts(external_temp)

        # Expected: 0.33 × 1.5 ACH × 30m³ × 23K = 341.55W
        expected = 0.33 * 1.5 * 30 * (21 - (-2))
        assert abs(vent_loss - expected) < 0.1

    def test_total_heat_loss(self):
        """Test total heat loss calculation."""
        room = Room(
            name='Living Room',
            room_type='Lounge',
            design_temp=21,
            volume=60,
            air_change_rate=1.0
        )

        room.walls.append(Wall('Wall 1', area=20, u_value=0.3))
        room.windows.append(Window('Window 1', area=4, u_value=1.4))
        room.floors.append(Floor('Floor', area=25, u_value=0.25, temperature_factor=0.5))

        external_temp = -2
        total_loss = room.total_heat_loss_watts(external_temp)

        # Should be sum of fabric and ventilation
        fabric = room.fabric_heat_loss_watts(external_temp)
        vent = room.ventilation_heat_loss_watts(external_temp)

        assert abs(total_loss - (fabric['total'] + vent)) < 0.1

    def test_thermal_bridging(self):
        """Test thermal bridging calculation."""
        room = Room(
            name='Test Room',
            room_type='Lounge',
            design_temp=21,
            volume=30,
            thermal_bridging_factor=0.15
        )

        room.walls.append(Wall('Wall', area=10, u_value=0.3))

        external_temp = -2
        fabric_loss = room.fabric_heat_loss_watts(external_temp)

        # Thermal bridging should be 15% of base fabric loss
        base_loss = fabric_loss['walls'] + fabric_loss['windows'] + fabric_loss['floors']
        expected_bridging = base_loss * 0.15

        assert abs(fabric_loss['thermal_bridging'] - expected_bridging) < 0.1


class TestHeatPumpCalculator:
    """Test main calculator functionality."""

    def test_calculator_initialization(self):
        """Test calculator initialization."""
        calc = HeatPumpCalculator(postcode_area='SW')

        assert calc.postcode_area == 'SW'
        assert calc.degree_days == 2033
        assert calc.design_external_temp == -2.0

    def test_invalid_postcode(self):
        """Test invalid postcode raises error."""
        with pytest.raises(ValueError):
            HeatPumpCalculator(postcode_area='XX')

    def test_create_building(self):
        """Test building creation."""
        calc = HeatPumpCalculator(postcode_area='M')
        building = calc.create_building('Test House')

        assert building.name == 'Test House'
        assert building.postcode_area == 'M'

    def test_create_room(self):
        """Test room creation with defaults."""
        calc = HeatPumpCalculator(postcode_area='SW')
        room = calc.create_room(
            name='Living Room',
            room_type='Lounge',
            floor_area=25,
            height=2.4
        )

        assert room.name == 'Living Room'
        assert room.design_temp == 21  # Default for Lounge
        assert room.volume == 60  # 25 × 2.4

    def test_hot_water_calculation(self):
        """Test hot water energy calculation."""
        calc = HeatPumpCalculator(postcode_area='SW')

        hw_energy = calc.calculate_hot_water_energy(
            num_occupants=4,
            daily_usage_litres=200,
            cold_water_temp=10,
            hot_water_temp=60
        )

        # Expected daily: 200L × 50K × 1.163 Wh/L·K / 1000 = 11.63 kWh
        expected_daily = 200 * 50 * 1.163 / 1000
        assert abs(hw_energy['daily_energy_kwh'] - expected_daily) < 0.1

        # Annual should be daily × 365
        expected_annual = expected_daily * 365
        assert abs(hw_energy['annual_energy_kwh'] - expected_annual) < 0.1

    def test_heat_pump_sizing(self):
        """Test heat pump sizing calculation."""
        calc = HeatPumpCalculator(postcode_area='SW')

        sizing = calc.size_heat_pump(
            design_heat_loss_kw=8.5,
            hot_water_demand_kw=3.0,
            oversizing_factor=1.1
        )

        expected_capacity = (8.5 + 3.0) * 1.1
        assert abs(sizing['required_capacity_kw'] - expected_capacity) < 0.01

    def test_annual_energy_consumption(self):
        """Test annual energy consumption calculation."""
        calc = HeatPumpCalculator(postcode_area='SW')

        energy = calc.calculate_annual_energy_consumption(
            space_heating_kwh=10000,
            hot_water_kwh=3000,
            cop=3.5
        )

        expected_total = 10000 + 3000
        expected_electricity = expected_total / 3.5

        assert energy['total_heat_demand_kwh'] == expected_total
        assert abs(energy['electricity_consumption_kwh'] - expected_electricity) < 0.1

    def test_radiator_sizing(self):
        """Test radiator sizing for low temp system."""
        calc = HeatPumpCalculator(postcode_area='SW')

        rad_sizing = calc.calculate_radiator_sizing(
            room_heat_loss_w=1500,
            room_temp=21,
            flow_temp=45,
            return_temp=40
        )

        # Mean water temp = 42.5°C
        # Delta T = 42.5 - 21 = 21.5°C
        assert rad_sizing['mean_water_temp'] == 42.5
        assert rad_sizing['delta_t'] == 21.5

        # Radiator needs to be larger for low temp systems
        assert rad_sizing['sizing_factor'] > 1.0


class TestIntegration:
    """Integration tests with complete building."""

    def test_complete_building_calculation(self):
        """Test complete building heat loss calculation."""
        # Create calculator for London (SW postcode)
        calc = HeatPumpCalculator(postcode_area='SW', building_category='B')

        # Create building
        building = calc.create_building('Test House')

        # Create living room
        living_room = calc.create_room(
            name='Living Room',
            room_type='Lounge',
            floor_area=25,
            height=2.4
        )

        # Add fabric elements
        living_room.walls.append(Wall('External Wall', area=15, u_value=0.3))
        living_room.windows.append(Window('Window', area=4, u_value=1.4))
        living_room.floors.append(Floor('Ground Floor', area=25, u_value=0.25, temperature_factor=0.5))
        living_room.thermal_bridging_factor = 0.15

        building.add_room(living_room)

        # Create bedroom
        bedroom = calc.create_room(
            name='Bedroom 1',
            room_type='Bedroom',
            floor_area=15,
            height=2.4
        )

        bedroom.walls.append(Wall('External Wall', area=10, u_value=0.3))
        bedroom.windows.append(Window('Window', area=2, u_value=1.4))
        bedroom.floors.append(Floor('Ground Floor', area=15, u_value=0.25, temperature_factor=0.5))
        bedroom.thermal_bridging_factor = 0.15

        building.add_room(bedroom)

        # Calculate heat loss
        summary = calc.calculate_building_heat_loss()

        # Verify structure
        assert summary['building_name'] == 'Test House'
        assert summary['num_rooms'] == 2
        assert summary['external_temp'] == -2.0
        assert summary['degree_days'] == 2033

        # Verify heat loss is calculated
        assert summary['total_heat_loss']['watts'] > 0
        assert summary['total_heat_loss']['kwh'] > 0

        # Room summaries should be present
        assert len(summary['rooms']) == 2
        assert summary['rooms'][0]['room_name'] == 'Living Room'
        assert summary['rooms'][1]['room_name'] == 'Bedroom 1'

    def test_full_system_design(self):
        """Test full heat pump system design."""
        calc = HeatPumpCalculator(postcode_area='M', building_category='B')

        # Location info
        location = calc.get_location_info()
        assert location['postcode_area'] == 'M'
        assert location['design_external_temp'] == -3.1

        # Create simple building
        building = calc.create_building('Manchester House')
        room = calc.create_room('Lounge', 'Lounge', floor_area=20)
        room.walls.append(Wall('Wall', area=20, u_value=0.3))
        room.windows.append(Window('Window', area=3, u_value=1.4))
        room.floors.append(Floor('Floor', area=20, u_value=0.25))
        building.add_room(room)

        # Calculate heat loss
        summary = calc.calculate_building_heat_loss()
        design_heat_loss_kw = summary['total_heat_loss']['watts'] / 1000

        # Hot water
        hw_energy = calc.calculate_hot_water_energy(num_occupants=4)

        # Size heat pump
        sizing = calc.size_heat_pump(
            design_heat_loss_kw=design_heat_loss_kw,
            hot_water_demand_kw=3.0
        )

        # Annual energy
        annual_energy = calc.calculate_annual_energy_consumption(
            space_heating_kwh=summary['total_heat_loss']['kwh'],
            hot_water_kwh=hw_energy['annual_energy_kwh'],
            cop=3.0
        )

        # Verify all calculations completed
        assert sizing['required_capacity_kw'] > 0
        assert annual_energy['electricity_consumption_kwh'] > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
