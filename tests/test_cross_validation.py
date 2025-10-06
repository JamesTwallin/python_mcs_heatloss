"""Cross-validation tests comparing formula outputs with known values."""
import pytest
from mcs_calculator import HeatPumpCalculator, Room, Wall, Window, Floor
from mcs_calculator.data_tables import DegreeDays
import math


class TestFormulaAccuracy:
    """Test that formulas produce mathematically correct results."""

    def test_fabric_loss_formula_precision(self):
        """Test fabric heat loss formula Q = A × U × ΔT."""
        room = Room('Test', 'Lounge', design_temp=21, volume=60)
        room.walls.append(Wall('Wall', area=10, u_value=0.3))

        # ΔT = 21 - (-2) = 23K
        # Q = 10 × 0.3 × 23 = 69W
        loss = room.fabric_heat_loss_watts(-2)
        expected = 10 * 0.3 * 23
        assert abs(loss['walls'] - expected) < 0.001, f"Expected {expected}, got {loss['walls']}"

    def test_ventilation_loss_formula_precision(self):
        """Test ventilation loss formula Q = 0.33 × n × V × ΔT."""
        room = Room('Test', 'Lounge', design_temp=21, volume=60, air_change_rate=1.5)

        # Q = 0.33 × 1.5 × 60 × 23 = 683.1W
        loss = room.ventilation_heat_loss_watts(-2)
        expected = 0.33 * 1.5 * 60 * 23
        assert abs(loss - expected) < 0.001, f"Expected {expected}, got {loss}"

    def test_thermal_bridging_percentage(self):
        """Test thermal bridging is exactly 15% of base fabric."""
        room = Room('Test', 'Lounge', design_temp=21, volume=60, thermal_bridging_factor=0.15)
        room.walls.append(Wall('Wall', area=20, u_value=0.3))

        fabric = room.fabric_heat_loss_watts(-2)
        base = fabric['walls'] + fabric['windows'] + fabric['floors']
        expected_tb = base * 0.15

        assert abs(fabric['thermal_bridging'] - expected_tb) < 0.001

    def test_ground_floor_temperature_factor(self):
        """Test ground floor applies 0.5 temperature factor correctly."""
        room = Room('Test', 'Lounge', design_temp=21, volume=60)
        room.floors.append(Floor('Floor', area=30, u_value=0.25, temperature_factor=0.5))

        # Q = 30 × 0.25 × 23 × 0.5 = 86.25W
        fabric = room.fabric_heat_loss_watts(-2)
        expected = 30 * 0.25 * 23 * 0.5
        assert abs(fabric['floors'] - expected) < 0.001


class TestKnownScenarios:
    """Test against known realistic scenarios."""

    def test_typical_living_room_heat_loss(self):
        """Test typical living room gives realistic heat loss."""
        calc = HeatPumpCalculator('M')
        room = calc.create_room('Living Room', 'Lounge', floor_area=25, height=2.4)

        # Typical fabric for modern build
        room.walls.append(Wall('Wall', area=20, u_value=0.28))
        room.windows.append(Window('Window', area=4, u_value=1.4))
        room.floors.append(Floor('Floor', area=25, u_value=0.22, temperature_factor=0.5))
        room.thermal_bridging_factor = 0.15

        total_loss = room.total_heat_loss_watts(-3.1)

        # Expect 600-1200W for typical living room in Manchester
        assert 600 < total_loss < 1200, f"Living room loss {total_loss}W outside expected range"

    def test_typical_bedroom_heat_loss(self):
        """Test typical bedroom gives realistic heat loss."""
        calc = HeatPumpCalculator('SW')
        room = calc.create_room('Bedroom', 'Bedroom', floor_area=12, height=2.4)

        room.walls.append(Wall('Wall', area=12, u_value=0.28))
        room.windows.append(Window('Window', area=2, u_value=1.4))
        room.floors.append(Floor('Floor', area=12, u_value=0.22, temperature_factor=0.5))
        room.thermal_bridging_factor = 0.15

        total_loss = room.total_heat_loss_watts(-2.0)

        # Expect 250-550W for typical bedroom in London
        assert 250 < total_loss < 550, f"Bedroom loss {total_loss}W outside expected range"

    def test_bathroom_higher_temperature(self):
        """Test bathroom with higher design temp has higher heat loss."""
        calc = HeatPumpCalculator('M')

        bedroom = calc.create_room('Bedroom', 'Bedroom', floor_area=10, height=2.4)
        bedroom.walls.append(Wall('Wall', area=10, u_value=0.28))
        bedroom.floors.append(Floor('Floor', area=10, u_value=0.22, temperature_factor=0.5))

        bathroom = calc.create_room('Bathroom', 'Bathroom', floor_area=10, height=2.4)
        bathroom.walls.append(Wall('Wall', area=10, u_value=0.28))
        bathroom.floors.append(Floor('Floor', area=10, u_value=0.22, temperature_factor=0.5))

        bedroom_loss = bedroom.total_heat_loss_watts(-3.1)
        bathroom_loss = bathroom.total_heat_loss_watts(-3.1)

        # Bathroom (22°C) should have higher loss than bedroom (18°C)
        assert bathroom_loss > bedroom_loss

    def test_cold_climate_higher_design_loss(self):
        """Test colder climate has higher design heat loss."""
        # Same house in two locations
        # London (SW): -2°C
        calc_sw = HeatPumpCalculator('SW')
        room_sw = calc_sw.create_room('Room', 'Lounge', floor_area=20, height=2.4)
        room_sw.walls.append(Wall('Wall', area=15, u_value=0.28))
        room_sw.floors.append(Floor('Floor', area=20, u_value=0.22, temperature_factor=0.5))

        # Aberdeen (AB): -4.2°C
        calc_ab = HeatPumpCalculator('AB')
        room_ab = calc_ab.create_room('Room', 'Lounge', floor_area=20, height=2.4)
        room_ab.walls.append(Wall('Wall', area=15, u_value=0.28))
        room_ab.floors.append(Floor('Floor', area=20, u_value=0.22, temperature_factor=0.5))

        loss_sw = room_sw.total_heat_loss_watts(calc_sw.design_external_temp)
        loss_ab = room_ab.total_heat_loss_watts(calc_ab.design_external_temp)

        # Aberdeen should have higher design loss due to colder external temp
        assert loss_ab > loss_sw

    def test_cold_climate_higher_annual_energy(self):
        """Test colder climate has higher annual energy despite same design loss."""
        # Create identical rooms
        calc_sw = HeatPumpCalculator('SW')  # DD = 2033
        room_sw = calc_sw.create_room('Room', 'Lounge', floor_area=20, height=2.4)
        room_sw.walls.append(Wall('Wall', area=15, u_value=0.28))

        calc_ab = HeatPumpCalculator('AB')  # DD = 2668
        room_ab = calc_ab.create_room('Room', 'Lounge', floor_area=20, height=2.4)
        room_ab.walls.append(Wall('Wall', area=15, u_value=0.28))

        kwh_sw = room_sw.total_heat_loss_kwh(
            calc_sw.design_external_temp,
            calc_sw.degree_days
        )
        kwh_ab = room_ab.total_heat_loss_kwh(
            calc_ab.design_external_temp,
            calc_ab.degree_days
        )

        # Aberdeen should have higher annual energy due to more degree days
        assert kwh_ab > kwh_sw


class TestCompleteBuildings:
    """Test complete building scenarios."""

    def test_small_bungalow_realistic_output(self):
        """Test small bungalow gives realistic total heat loss."""
        calc = HeatPumpCalculator('M')
        building = calc.create_building('Small Bungalow')

        # 4 small rooms
        for i, (name, rtype, area) in enumerate([
            ('Living Room', 'Lounge', 20),
            ('Bedroom', 'Bedroom', 12),
            ('Kitchen', 'Kitchen', 10),
            ('Bathroom', 'Bathroom', 5)
        ]):
            room = calc.create_room(name, rtype, floor_area=area)
            room.walls.append(Wall('Wall', area=area*0.6, u_value=0.28))
            room.windows.append(Window('Window', area=area*0.08, u_value=1.4))
            room.floors.append(Floor('Floor', area=area, u_value=0.22, temperature_factor=0.5))
            room.thermal_bridging_factor = 0.15
            building.add_room(room)

        summary = calc.calculate_building_heat_loss()
        total_kw = summary['total_heat_loss']['watts'] / 1000

        # Small modern bungalow: expect 1.2-3.0 kW (modern insulation standards)
        assert 1.2 < total_kw < 3.0, f"Total {total_kw}kW outside expected range for small bungalow"

    def test_medium_house_realistic_output(self):
        """Test medium house gives realistic total heat loss."""
        calc = HeatPumpCalculator('SW')
        building = calc.create_building('Medium House')

        # 6 rooms
        for name, rtype, area in [
            ('Living Room', 'Lounge', 25),
            ('Kitchen', 'Kitchen', 16),
            ('Bedroom 1', 'Bedroom', 15),
            ('Bedroom 2', 'Bedroom', 12),
            ('Bedroom 3', 'Bedroom', 10),
            ('Bathroom', 'Bathroom', 6)
        ]:
            room = calc.create_room(name, rtype, floor_area=area)
            room.walls.append(Wall('Wall', area=area*0.5, u_value=0.30))
            room.windows.append(Window('Window', area=area*0.1, u_value=1.6))
            room.floors.append(Floor('Floor', area=area, u_value=0.25, temperature_factor=0.5))
            room.thermal_bridging_factor = 0.15
            building.add_room(room)

        summary = calc.calculate_building_heat_loss()
        total_kw = summary['total_heat_loss']['watts'] / 1000

        # Medium modern house: expect 2.0-5.0 kW (modern insulation standards)
        assert 2.0 < total_kw < 5.0, f"Total {total_kw}kW outside expected range for medium house"

    def test_hot_water_energy_realistic(self):
        """Test hot water energy is in realistic range."""
        calc = HeatPumpCalculator('M')

        # Family of 4
        hw = calc.calculate_hot_water_energy(num_occupants=4)

        # Expect 3500-5000 kWh/year for family of 4
        assert 3500 < hw['annual_energy_kwh'] < 5000

        # Single person
        hw_single = calc.calculate_hot_water_energy(num_occupants=1)

        # Expect 1000-1500 kWh/year for single person
        assert 1000 < hw_single['annual_energy_kwh'] < 1500

    def test_heat_pump_cop_affects_electricity(self):
        """Test that COP correctly affects electricity consumption."""
        calc = HeatPumpCalculator('SW')

        heat_demand = 10000  # 10,000 kWh heat

        energy_cop25 = calc.calculate_annual_energy_consumption(
            space_heating_kwh=heat_demand,
            hot_water_kwh=0,
            cop=2.5
        )

        energy_cop35 = calc.calculate_annual_energy_consumption(
            space_heating_kwh=heat_demand,
            hot_water_kwh=0,
            cop=3.5
        )

        # Higher COP should use less electricity
        assert energy_cop35['electricity_consumption_kwh'] < energy_cop25['electricity_consumption_kwh']

        # Check exact calculation
        expected_cop25 = heat_demand / 2.5
        expected_cop35 = heat_demand / 3.5

        assert abs(energy_cop25['electricity_consumption_kwh'] - expected_cop25) < 0.1
        assert abs(energy_cop35['electricity_consumption_kwh'] - expected_cop35) < 0.1


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_zero_fabric_elements(self):
        """Test room with no fabric elements (internal room)."""
        room = Room('Internal Room', 'Store', design_temp=15, volume=20)
        fabric = room.fabric_heat_loss_watts(-2)

        # Should be zero with no fabric elements
        assert fabric['total'] == 0

    def test_large_temperature_difference(self):
        """Test extreme temperature difference."""
        calc = HeatPumpCalculator('AB')  # Coldest UK location
        room = calc.create_room('Room', 'Lounge', floor_area=20)
        room.walls.append(Wall('Wall', area=10, u_value=0.3))

        # AB: -4.2°C, Lounge: 21°C, ΔT = 25.2K
        loss = room.total_heat_loss_watts(-4.2)

        # Should be proportionally higher
        assert loss > 0
        assert loss < 5000  # But still realistic for single room

    def test_very_well_insulated_building(self):
        """Test passive house standard building."""
        calc = HeatPumpCalculator('M')
        room = calc.create_room('Room', 'Lounge', floor_area=25, height=2.4)

        # Passive house U-values
        room.walls.append(Wall('Wall', area=20, u_value=0.15))  # Very low
        room.windows.append(Window('Window', area=3, u_value=0.8))  # Triple glazed
        room.floors.append(Floor('Floor', area=25, u_value=0.12, temperature_factor=0.5))
        room.thermal_bridging_factor = 0.05  # Minimal bridging
        room.air_change_rate = 0.3  # MVHR system

        loss = room.total_heat_loss_watts(-3.1)

        # Should be very low heat loss
        assert loss < 400, "Passive house should have very low heat loss"


class TestAnnualEnergyCalculations:
    """Test annual energy calculations with degree days."""

    def test_degree_days_scaling(self):
        """Test that annual energy scales with degree days."""
        # Same room in different locations
        room = Room('Room', 'Lounge', design_temp=21, volume=60)
        room.walls.append(Wall('Wall', area=15, u_value=0.3))

        # London: DD = 2033
        kwh_sw = room.total_heat_loss_kwh(external_temp=-2.0, degree_days=2033)

        # Manchester: DD = 2275
        kwh_m = room.total_heat_loss_kwh(external_temp=-3.1, degree_days=2275)

        # Higher degree days should give higher annual energy
        assert kwh_m > kwh_sw

        # Ratio should be approximately DD_m / DD_sw
        ratio = kwh_m / kwh_sw if kwh_sw > 0 else 0
        expected_ratio = 2275 / 2033

        # Allow 5% tolerance due to different external temps
        assert abs(ratio - expected_ratio) / expected_ratio < 0.05


class TestRadiatorSizing:
    """Test radiator sizing calculations."""

    def test_low_temp_needs_larger_radiators(self):
        """Test low temperature systems need larger radiators."""
        calc = HeatPumpCalculator('M')

        # High temp boiler system (70/50)
        high_temp = calc.calculate_radiator_sizing(
            room_heat_loss_w=1000,
            room_temp=21,
            flow_temp=70,
            return_temp=50
        )

        # Low temp heat pump (45/40)
        low_temp = calc.calculate_radiator_sizing(
            room_heat_loss_w=1000,
            room_temp=21,
            flow_temp=45,
            return_temp=40
        )

        # Low temp needs larger radiator
        assert low_temp['sizing_factor'] > high_temp['sizing_factor']
        assert low_temp['required_output_at_delta_t_50'] > high_temp['required_output_at_delta_t_50']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
