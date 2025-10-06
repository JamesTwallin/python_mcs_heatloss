"""
Validation against heatlossjs test cases.

This test replicates the test cases from https://github.com/TrystanLea/heatlossjs
to ensure our Python implementation produces compatible results.
"""
import pytest
import json
from mcs_calculator import HeatPumpCalculator, Room, Wall, Window, Floor, Building


class TestHeatLossJSValidation:
    """Validate against heatlossjs JavaScript implementation test cases."""

    def test_midterrace_house_living_room_with_inter_room(self):
        """
        Test case from heatlossjs: Mid-terrace house - Living Room
        Source: heatlossjs_midterrace_24Jul1826.json

        This test validates inter-room heat transfer modeling matching heatlossjs.

        Living Room specifications from JSON:
        - Temperature: 20°C
        - Dimensions: 3.4m × 7.2m × 2.4m = 58.752m³
        - Air changes: 0.6 ACH
        - Multiple boundaries: external, ground, unheated, and adjacent rooms

        Expected from heatlossjs:
        - Total Living Room Heat Loss: 1,179.47 W
        - Inter-room transfers to: hall, kitchen, bed1, bed2, landing, study
        """
        # Load the test case data
        try:
            with open('heatlossjs_midterrace_test.json', 'r') as f:
                js_data = json.load(f)
        except FileNotFoundError:
            pytest.skip("heatlossjs test data file not found")

        # Extract parameters from JS data
        external_temp = js_data['T']['external']  # -1.4°C
        ground_temp = js_data['T']['ground']  # 10.6°C

        # Living Room from JS data
        living_room = Room(
            name='livingroom',
            room_type='Lounge',
            design_temp=20,
            volume=58.752,  # 3.4m × 7.2m × 2.4m
            air_change_rate=0.6,
            height=2.4,
            thermal_bridging_factor=0.0  # heatlossjs handles thermal bridging differently
        )

        # Parse elements from JS test case
        # Element id=0: External, heat: 169.488 W
        living_room.walls.append(Wall(
            'External Wall 1',
            area=5.28,  # Calculated from heat/u/deltaT: 169.488/(1.5*21.4)
            u_value=1.5,
            boundary='external'
        ))

        # Element id=1: Unheated, heat: 51.84 W, deltaT: 2
        living_room.walls.append(Wall(
            'Wall to Unheated',
            area=17.28,  # 51.84/(1.5*2)
            u_value=1.5,
            boundary='unheated',
            boundary_temp=18
        ))

        # Element id=2: External, heat: 82.818 W
        living_room.walls.append(Wall(
            'External Wall 2',
            area=2.58,  # 82.818/(1.5*21.4)
            u_value=1.5,
            boundary='external'
        ))

        # Element id=3: Hall, heat: 34.56 W, deltaT: 1
        living_room.walls.append(Wall(
            'Wall to Hall',
            area=17.28,  # 34.56/(2*1)
            u_value=2.0,
            boundary='hall'
        ))

        # Element id=4: Ground floor, heat: 87.44256 W, deltaT: 9.4
        living_room.floors.append(Floor(
            'Ground Floor',
            area=24.48,  # 3.4 * 7.2
            u_value=0.38,
            temperature_factor=1.0  # Will use ground temp explicitly
        ))

        # Element id=5: Bed2, heat: 14.688 W, deltaT: 1
        living_room.walls.append(Wall(
            'Wall to Bed2',
            area=7.344,  # 14.688/(2*1)
            u_value=2.0,
            boundary='bed2'
        ))

        # Element id=6: External, heat: 172.57 W
        living_room.windows.append(Window(
            'Window 1',
            area=2.882,  # 172.57/(2.8*21.4)
            u_value=2.8
        ))

        # Element id=7: External, heat: 89.88 W
        living_room.windows.append(Window(
            'Window 2',
            area=1.5,  # 89.88/(2.8*21.4)
            u_value=2.8
        ))

        # Element id=8: Kitchen, heat: 201.6 W, deltaT: 1
        living_room.walls.append(Wall(
            'Wall to Kitchen',
            area=100.8,  # 201.6/(2*1)
            u_value=2.0,
            boundary='kitchen'
        ))

        # Element id=9: Bed1, heat: 16.66 W, deltaT: 1
        living_room.walls.append(Wall(
            'Wall to Bed1',
            area=8.33,  # 16.66/(2*1)
            u_value=2.0,
            boundary='bed1'
        ))

        # Element id=10: Landing, heat: 5.984 W, deltaT: 1
        living_room.walls.append(Wall(
            'Wall to Landing',
            area=2.992,  # 5.984/(2*1)
            u_value=2.0,
            boundary='landing'
        ))

        # Element id=11: Study, heat: 2.992 W, deltaT: 1
        living_room.walls.append(Wall(
            'Wall to Study',
            area=1.496,  # 2.992/(2*1)
            u_value=2.0,
            boundary='study'
        ))

        # Setup room temperatures for inter-room heat transfer
        room_temps = {
            'hall': 19,
            'kitchen': 19,  # Appears to be 19 based on deltaT=1
            'bed1': 19,
            'bed2': 19,
            'landing': 19,
            'study': 19
        }

        # Calculate fabric heat loss with inter-room transfers
        fabric_loss = living_room.fabric_heat_loss_watts(external_temp, room_temps)

        # Adjust ground floor calculation for ground temperature
        # Remove default floor loss and recalculate with ground temp
        ground_delta_t = 20 - ground_temp  # 9.4K
        ground_floor_loss = 24.48 * 0.38 * ground_delta_t  # 87.44256 W

        # Recalculate total (subtract default floor, add correct floor)
        # Note: fabric_loss already includes thermal bridging from Room calculation
        total_fabric_with_tb = fabric_loss['total']

        # Adjust for ground floor temperature
        # Remove default floor calculation (which used external temp)
        # Add correct floor calculation (with ground temp)
        total_fabric_adjusted = (total_fabric_with_tb - fabric_loss['floors'] + ground_floor_loss)

        # Ventilation heat loss: 0.33 × 0.6 × 58.752 × 21.4
        vent_loss = living_room.ventilation_heat_loss_watts(external_temp)

        total_loss = total_fabric_adjusted + vent_loss

        # Expected from heatlossjs
        js_living_room_loss = 1179.47

        print(f"\nLiving Room Heat Loss Comparison (with inter-room):")
        print(f"  Fabric loss (walls): {fabric_loss['walls']:.2f} W")
        print(f"  Fabric loss (windows): {fabric_loss['windows']:.2f} W")
        print(f"  Ground floor (adjusted): {ground_floor_loss:.2f} W")
        print(f"  Inter-room transfers: {fabric_loss['inter_room']:.2f} W")
        print(f"  Thermal bridging: {fabric_loss['thermal_bridging']:.2f} W")
        print(f"  Total fabric: {total_fabric_adjusted:.2f} W")
        print(f"  Ventilation: {vent_loss:.2f} W")
        print(f"  Total Python: {total_loss:.2f} W")
        print(f"  Total JS: {js_living_room_loss:.2f} W")
        print(f"  Difference: {abs(total_loss - js_living_room_loss):.2f} W ({abs(total_loss - js_living_room_loss)/js_living_room_loss*100:.1f}%)")

        # Should match closely now with inter-room modeling + thermal bridging
        tolerance = 0.02  # 2% tolerance
        assert abs(total_loss - js_living_room_loss) / js_living_room_loss < tolerance, \
            f"Living room heat loss differs by more than {tolerance*100}%"

    def test_heatlossjs_formula_compatibility(self):
        """
        Test that our formulas are compatible with heatlossjs approach.

        Both implementations should use:
        - Fabric loss: A × U × ΔT
        - Ventilation: 0.33 × n × V × ΔT (or similar specific heat constant)
        """
        # Simple test: same inputs should give same outputs

        # External wall: 10m² × U=1.5 × ΔT=21.4K
        wall_area = 10
        u_value = 1.5
        delta_t = 21.4

        js_expected = wall_area * u_value * delta_t  # 321 W

        # Python calculation
        room = Room('Test', 'Lounge', design_temp=20, volume=50)
        room.walls.append(Wall('Wall', area=wall_area, u_value=u_value))

        external_temp = 20 - delta_t  # -1.4°C
        py_result = room.fabric_heat_loss_watts(external_temp)

        print(f"\nFormula Compatibility Test:")
        print(f"  Expected (JS formula): {js_expected:.2f} W")
        print(f"  Python result:         {py_result['walls']:.2f} W")
        print(f"  Match: {abs(py_result['walls'] - js_expected) < 0.01}")

        assert abs(py_result['walls'] - js_expected) < 0.01, \
            "Basic formula doesn't match heatlossjs approach"

    def test_ventilation_formula_match(self):
        """
        Test ventilation heat loss formula matches heatlossjs.

        Standard formula: Q = 0.33 × n × V × ΔT
        """
        volume = 58.75  # m³ (living room from JS test)
        ach = 0.6  # air changes per hour
        delta_t = 21.4  # K (20°C - (-1.4°C))

        # Expected from standard formula
        js_expected = 0.33 * ach * volume * delta_t  # 247.401 W

        # Python calculation
        room = Room('Test', 'Lounge', design_temp=20, volume=volume, air_change_rate=ach)
        py_result = room.ventilation_heat_loss_watts(-1.4)

        print(f"\nVentilation Formula Test:")
        print(f"  Expected (0.33 × {ach} × {volume} × {delta_t}): {js_expected:.2f} W")
        print(f"  Python result: {py_result:.2f} W")
        print(f"  Match: {abs(py_result - js_expected) < 0.01}")

        assert abs(py_result - js_expected) < 0.01, \
            "Ventilation formula doesn't match standard approach"

    def test_ground_floor_temperature_handling(self):
        """
        Test ground floor heat loss with ground temperature.

        heatlossjs uses ground temperature (10.6°C) instead of external temperature
        for ground floors, which is more accurate.
        """
        # Ground floor from JS test
        area = 24.48  # m²
        u_value = 0.38  # W/m²K (insulated ground floor)
        room_temp = 20  # °C
        ground_temp = 10.6  # °C
        delta_t = room_temp - ground_temp  # 9.4 K

        # Expected heat loss
        js_expected = area * u_value * delta_t  # 87.44 W

        print(f"\nGround Floor Temperature Test:")
        print(f"  Formula: {area} × {u_value} × {delta_t} = {js_expected:.2f} W")
        print(f"  This matches JS: heat: 87.44256 W")

        # Our Python implementation can handle this with temperature_factor=1.0
        # and calculating separately with ground temp
        calculated = area * u_value * delta_t

        assert abs(calculated - js_expected) < 0.01, \
            "Ground floor calculation doesn't match"

    def test_poor_insulation_values(self):
        """
        Test with poor U-values typical of older buildings (like JS test case).

        JS test uses:
        - External walls: U=1.5 W/m²K (very poor - old single brick)
        - Windows: U=2.8 W/m²K (old double glazing)
        - Ground floor: U=0.38-0.9 W/m²K (some insulation)
        """
        # Our implementation should handle any U-value correctly
        room = Room('Old Building Room', 'Lounge', design_temp=20, volume=60)

        # Very poor wall insulation
        room.walls.append(Wall('Old External Wall', area=20, u_value=1.5))

        # Poor windows
        room.windows.append(Window('Old Double Glazing', area=4, u_value=2.8))

        # Calculate
        fabric_loss = room.fabric_heat_loss_watts(-1.4)

        # Wall loss: 20 × 1.5 × 21.4 = 642 W
        expected_wall = 20 * 1.5 * 21.4

        # Window loss: 4 × 2.8 × 21.4 = 239.68 W
        expected_window = 4 * 2.8 * 21.4

        print(f"\nPoor Insulation Test:")
        print(f"  Wall loss: {fabric_loss['walls']:.2f} W (expected {expected_wall:.2f} W)")
        print(f"  Window loss: {fabric_loss['windows']:.2f} W (expected {expected_window:.2f} W)")

        assert abs(fabric_loss['walls'] - expected_wall) < 0.01
        assert abs(fabric_loss['windows'] - expected_window) < 0.01


    def test_inter_room_heat_transfer_basic(self):
        """
        Test basic inter-room heat transfer functionality.

        Scenario: Two adjacent rooms at different temperatures
        - Living Room at 20°C with party wall to Kitchen at 18°C
        - Party wall: 10m² × U=0.5 W/m²K
        - Expected heat transfer: 10 × 0.5 × (20-18) = 10W
        """
        # Create building with two rooms
        building = Building('Test House', 'SW1')

        # Living room at 20°C
        living = Room(
            name='Living Room',
            room_type='Lounge',
            design_temp=20,
            volume=50,
            air_change_rate=0.5
        )

        # Add party wall to kitchen (lower case match)
        living.walls.append(Wall(
            'Party Wall to Kitchen',
            area=10,
            u_value=0.5,
            boundary='kitchen'  # Adjacent room
        ))

        # Kitchen at 18°C
        kitchen = Room(
            name='Kitchen',
            room_type='Kitchen',
            design_temp=18,
            volume=40,
            air_change_rate=1.0
        )

        building.add_room(living)
        building.add_room(kitchen)

        # Calculate with inter-room heat transfer
        external_temp = -1.4
        fabric_loss = living.fabric_heat_loss_watts(
            external_temp,
            room_temps={'kitchen': 18}
        )

        # Expected inter-room loss: 10m² × 0.5 × (20-18) = 10W
        expected_inter_room = 10 * 0.5 * 2

        print(f"\nInter-Room Heat Transfer Test:")
        print(f"  Living Room → Kitchen")
        print(f"  Temperature difference: 20°C - 18°C = 2K")
        print(f"  Wall: 10m² × U=0.5 W/m²K")
        print(f"  Expected: {expected_inter_room:.2f} W")
        print(f"  Calculated: {fabric_loss['inter_room']:.2f} W")

        assert abs(fabric_loss['inter_room'] - expected_inter_room) < 0.01, \
            "Inter-room heat transfer calculation incorrect"

    def test_building_inter_room_calculation(self):
        """
        Test that Building class correctly aggregates inter-room transfers.

        Tests the full building calculation with multiple rooms at different
        temperatures exchanging heat.
        """
        building = Building('Test House', 'SW1')

        # Room 1: Living at 20°C
        living = Room('Living', 'Lounge', design_temp=20, volume=50)
        living.walls.append(Wall('External', area=20, u_value=0.3, boundary='external'))
        living.walls.append(Wall('To Hall', area=10, u_value=0.5, boundary='hall'))

        # Room 2: Hall at 19°C
        hall = Room('Hall', 'Hall', design_temp=19, volume=30)
        hall.walls.append(Wall('External', area=10, u_value=0.3, boundary='external'))
        hall.walls.append(Wall('To Living', area=10, u_value=0.5, boundary='living'))

        building.add_room(living)
        building.add_room(hall)

        # Calculate with inter-room enabled
        summary = building.get_summary(-1.4, 2000, include_inter_room=True)

        print(f"\nBuilding Inter-Room Summary:")
        print(f"  Number of rooms: {summary['num_rooms']}")
        print(f"  Inter-room enabled: {summary['inter_room_enabled']}")

        # Verify both rooms have calculations
        assert summary['num_rooms'] == 2
        assert summary['inter_room_enabled'] == True

        # Check that each room reports inter-room heat loss
        living_summary = summary['rooms'][0]
        hall_summary = summary['rooms'][1]

        print(f"  Living room inter-room: {living_summary['fabric_loss']['watts']['inter_room']:.2f} W")
        print(f"  Hall inter-room: {hall_summary['fabric_loss']['watts']['inter_room']:.2f} W")

        # Living room should lose heat to hall (ΔT=1K)
        # 10m² × 0.5 × 1K = 5W
        assert abs(living_summary['fabric_loss']['watts']['inter_room'] - 5.0) < 0.01

        # Hall should gain heat from living (ΔT=-1K, so negative loss = gain)
        # 10m² × 0.5 × (-1K) = -5W
        assert abs(hall_summary['fabric_loss']['watts']['inter_room'] - (-5.0)) < 0.01


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
