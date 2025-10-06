"""Test web interface data compatibility with Python calculator."""
import json
import pytest
from mcs_calculator.room import Room, Wall, Window, Floor, Building


class TestWebDataCompatibility:
    """Test that web interface JSON data works with Python calculator."""

    def test_room_with_visualization_fields(self):
        """Python should ignore visualization fields from web interface."""
        room_data = {
            'name': 'Lounge',
            'room_type': 'Lounge',
            'design_temp': 21,
            'volume': 48,
            'air_change_rate': 1.0,
            'thermal_bridging_factor': 0.15,
            'height': 2.4,
            # Web-only fields
            'width': 5.0,
            'depth': 4.0,
            'position_x': 0.0,
            'position_z': 0.0,
            'walls': [],
            'windows': [],
            'floors': []
        }

        # Python should handle this gracefully
        room = Room(**{k: v for k, v in room_data.items()
                      if k in ['name', 'room_type', 'design_temp', 'volume',
                               'air_change_rate', 'thermal_bridging_factor', 'height']})

        assert room.name == 'Lounge'
        assert room.design_temp == 21
        assert room.volume == 48

    def test_window_with_wall_field(self):
        """Python should ignore 'wall' field from web interface."""
        window_data = {
            'name': 'Front Window',
            'area': 4.0,
            'u_value': 1.4,
            'wall': 'front'  # Web-only field
        }

        # Python Window only uses name, area, u_value
        window = Window(
            name=window_data['name'],
            area=window_data['area'],
            u_value=window_data['u_value']
        )

        assert window.name == 'Front Window'
        assert window.area == 4.0
        assert window.u_value == 1.4

        # Heat loss calculation should work
        heat_loss = window.heat_loss_watts(23)  # 23K temp diff
        expected = 4.0 * 1.4 * 23  # 128.8W
        assert abs(heat_loss - expected) < 0.01

    def test_complete_web_json_structure(self):
        """Test loading complete web JSON structure."""
        web_json = {
            'building_name': 'Test House',
            'postcode_area': 'M',
            'building_category': 'B',
            'external_temp': -3.1,
            'rooms': [
                {
                    'name': 'Lounge',
                    'room_type': 'Lounge',
                    'width': 5.0,
                    'depth': 4.0,
                    'height': 2.4,
                    'design_temp': 21,
                    'position_x': 0.0,
                    'position_z': 0.0,
                    'air_change_rate': 1.0,
                    'thermal_bridging': 15,
                    'walls': [
                        {
                            'name': 'North Wall',
                            'area': 12.0,
                            'u_value': 0.3,
                            'boundary': 'external',
                            'temperature_factor': 1.0
                        }
                    ],
                    'windows': [
                        {
                            'name': 'Front Window',
                            'area': 4.0,
                            'u_value': 1.4,
                            'wall': 'front'
                        }
                    ],
                    'floors': [
                        {
                            'name': 'Ground Floor',
                            'area': 20.0,
                            'u_value': 0.25,
                            'temperature_factor': 0.5
                        }
                    ]
                }
            ]
        }

        # Extract room data
        room_data = web_json['rooms'][0]

        # Create Python objects
        walls = [Wall(**w) for w in room_data['walls']]
        windows = [Window(name=w['name'], area=w['area'], u_value=w['u_value'])
                   for w in room_data['windows']]
        floors = [Floor(**f) for f in room_data['floors']]

        volume = room_data['width'] * room_data['depth'] * room_data['height']

        room = Room(
            name=room_data['name'],
            room_type=room_data['room_type'],
            design_temp=room_data['design_temp'],
            volume=volume,
            air_change_rate=room_data['air_change_rate'],
            thermal_bridging_factor=room_data['thermal_bridging'] / 100,
            height=room_data['height'],
            walls=walls,
            windows=windows,
            floors=floors
        )

        # Calculate heat loss
        external_temp = web_json['external_temp']
        fabric = room.fabric_heat_loss_watts(external_temp)
        vent = room.ventilation_heat_loss_watts(external_temp)
        total = fabric['total'] + vent

        # Verify calculations work
        assert fabric['total'] > 0
        assert vent > 0
        assert total > 0

    def test_inter_room_heat_transfer_compatibility(self):
        """Test inter-room heat transfer works with web data."""
        # Web JSON with adjacent rooms
        lounge_data = {
            'name': 'Lounge',
            'design_temp': 21,
            'volume': 48,
            'walls': [
                {
                    'name': 'Party Wall',
                    'area': 12.0,
                    'u_value': 0.5,
                    'boundary': 'Kitchen',  # Adjacent room
                    'temperature_factor': 1.0
                }
            ]
        }

        kitchen_data = {
            'name': 'Kitchen',
            'design_temp': 18,
            'volume': 30
        }

        # Create rooms
        lounge_wall = Wall(**lounge_data['walls'][0])
        lounge = Room(
            name=lounge_data['name'],
            room_type='Lounge',
            design_temp=lounge_data['design_temp'],
            volume=lounge_data['volume'],
            walls=[lounge_wall],
            windows=[],
            floors=[]
        )

        kitchen = Room(
            name=kitchen_data['name'],
            room_type='Kitchen',
            design_temp=kitchen_data['design_temp'],
            volume=kitchen_data['volume'],
            walls=[],
            windows=[],
            floors=[]
        )

        # Calculate with room temps
        room_temps = {kitchen.name: kitchen.design_temp}
        fabric = lounge.fabric_heat_loss_watts(-3, room_temps)

        # Inter-room loss: 12 * 0.5 * (21 - 18) = 18W
        assert abs(fabric['inter_room'] - 18.0) < 0.01

    def test_window_wall_positions(self):
        """Test that different wall positions don't affect calculations."""
        # Windows on different walls should have same heat loss
        windows = [
            {'name': 'Front Window', 'area': 4.0, 'u_value': 1.4, 'wall': 'front'},
            {'name': 'Back Window', 'area': 4.0, 'u_value': 1.4, 'wall': 'back'},
            {'name': 'Left Window', 'area': 4.0, 'u_value': 1.4, 'wall': 'left'},
            {'name': 'Right Window', 'area': 4.0, 'u_value': 1.4, 'wall': 'right'},
        ]

        temp_diff = 23
        for window_data in windows:
            window = Window(
                name=window_data['name'],
                area=window_data['area'],
                u_value=window_data['u_value']
            )
            heat_loss = window.heat_loss_watts(temp_diff)
            expected = 4.0 * 1.4 * 23  # 128.8W
            assert abs(heat_loss - expected) < 0.01, \
                f"{window_data['wall']} wall window has different heat loss"

    def test_building_with_web_positions(self):
        """Test Building class with web position data."""
        # Create rooms with positions
        room1_data = {
            'name': 'Room A1',
            'design_temp': 21,
            'volume': 48,
            'position_x': 0.0,
            'position_z': 0.0,
            'walls': [
                {'name': 'East Wall', 'area': 12, 'u_value': 0.5,
                 'boundary': 'Room A2', 'temperature_factor': 1.0}
            ]
        }

        room2_data = {
            'name': 'Room A2',
            'design_temp': 18,
            'volume': 48,
            'position_x': 5.0,
            'position_z': 0.0,
            'walls': [
                {'name': 'West Wall', 'area': 12, 'u_value': 0.5,
                 'boundary': 'Room A1', 'temperature_factor': 1.0}
            ]
        }

        # Create building
        room1 = Room(
            name=room1_data['name'],
            room_type='Lounge',
            design_temp=room1_data['design_temp'],
            volume=room1_data['volume'],
            walls=[Wall(**w) for w in room1_data['walls']],
            windows=[],
            floors=[]
        )

        room2 = Room(
            name=room2_data['name'],
            room_type='Kitchen',
            design_temp=room2_data['design_temp'],
            volume=room2_data['volume'],
            walls=[Wall(**w) for w in room2_data['walls']],
            windows=[],
            floors=[]
        )

        building = Building(name='Test Building', postcode_area='M', rooms=[room1, room2])
        summary = building.get_summary(-3, 2000, include_inter_room=True)

        # Should calculate without errors
        assert summary is not None
        assert 'inter_room_enabled' in summary
        assert summary['inter_room_enabled'] is True

    def test_json_round_trip(self):
        """Test data can round-trip through JSON."""
        # Create a room with Python
        room = Room(
            name='Test Room',
            room_type='Lounge',
            design_temp=21,
            volume=48,
            air_change_rate=1.0,
            thermal_bridging_factor=0.15,
            height=2.4,
            walls=[Wall('Wall', 12, 0.3, 1.0, 'external')],
            windows=[Window('Window', 4, 1.4)],
            floors=[Floor('Floor', 20, 0.25, 0.5)]
        )

        # Convert to dict (simulating JSON export)
        room_dict = {
            'name': room.name,
            'room_type': room.room_type,
            'design_temp': room.design_temp,
            'volume': room.volume,
            'air_change_rate': room.air_change_rate,
            'thermal_bridging': room.thermal_bridging_factor * 100,
            'height': room.height,
            'walls': [{'name': w.name, 'area': w.area, 'u_value': w.u_value,
                      'boundary': w.boundary, 'temperature_factor': w.temperature_factor}
                     for w in room.walls],
            'windows': [{'name': w.name, 'area': w.area, 'u_value': w.u_value}
                       for w in room.windows],
            'floors': [{'name': f.name, 'area': f.area, 'u_value': f.u_value,
                       'temperature_factor': f.temperature_factor}
                      for f in room.floors]
        }

        # Simulate web adding visualization fields
        room_dict['width'] = 5.0
        room_dict['depth'] = 4.0
        room_dict['position_x'] = 0.0
        room_dict['position_z'] = 0.0
        room_dict['windows'][0]['wall'] = 'front'

        # Convert back to Room (Python ignores extra fields)
        new_room = Room(
            name=room_dict['name'],
            room_type=room_dict['room_type'],
            design_temp=room_dict['design_temp'],
            volume=room_dict['volume'],
            air_change_rate=room_dict['air_change_rate'],
            thermal_bridging_factor=room_dict['thermal_bridging'] / 100,
            height=room_dict['height'],
            walls=[Wall(**w) for w in room_dict['walls']],
            windows=[Window(name=w['name'], area=w['area'], u_value=w['u_value'])
                    for w in room_dict['windows']],
            floors=[Floor(**f) for f in room_dict['floors']]
        )

        # Calculate heat loss for both - should be identical
        fabric1 = room.fabric_heat_loss_watts(-3)
        fabric2 = new_room.fabric_heat_loss_watts(-3)

        assert abs(fabric1['total'] - fabric2['total']) < 0.01

    def test_shell_subdivision_data(self):
        """Test data from web shell subdivision works in Python."""
        # Simulated data from subdivideShell() function
        shell_room = {
            'name': 'Room A1',
            'room_type': 'Lounge',
            'width': 4.0,
            'depth': 4.0,
            'height': 2.4,
            'design_temp': 21,
            'position_x': -2.0,
            'position_z': -2.0,
            'air_change_rate': None,
            'thermal_bridging': 15,
            'walls': [
                {'name': 'North Wall', 'area': 9.6, 'u_value': 0.3,
                 'boundary': 'external', 'temperature_factor': 1.0},
                {'name': 'South Wall', 'area': 9.6, 'u_value': 0.5,
                 'boundary': 'Room B1', 'temperature_factor': 1.0},
                {'name': 'West Wall', 'area': 9.6, 'u_value': 0.3,
                 'boundary': 'external', 'temperature_factor': 1.0},
                {'name': 'East Wall', 'area': 9.6, 'u_value': 0.5,
                 'boundary': 'Room A2', 'temperature_factor': 1.0}
            ],
            'windows': [],
            'floors': [
                {'name': 'Floor', 'area': 16.0, 'u_value': 0.25,
                 'temperature_factor': 0.5}
            ]
        }

        # Create room
        volume = shell_room['width'] * shell_room['depth'] * shell_room['height']
        room = Room(
            name=shell_room['name'],
            room_type=shell_room['room_type'],
            design_temp=shell_room['design_temp'],
            volume=volume,
            air_change_rate=shell_room['air_change_rate'] or 1.0,
            thermal_bridging_factor=shell_room['thermal_bridging'] / 100,
            height=shell_room['height'],
            walls=[Wall(**w) for w in shell_room['walls']],
            windows=[],
            floors=[Floor(**f) for f in shell_room['floors']]
        )

        # Should have 2 external walls and 2 adjacent room walls
        assert len(room.walls) == 4
        external_walls = [w for w in room.walls if w.boundary == 'external']
        adjacent_walls = [w for w in room.walls
                         if w.boundary not in ['external', 'ground', 'unheated']]

        assert len(external_walls) == 2
        assert len(adjacent_walls) == 2

        # Calculate heat loss
        room_temps = {'Room A2': 21, 'Room B1': 21}
        fabric = room.fabric_heat_loss_watts(-3, room_temps)

        # Should have inter-room component
        assert 'inter_room' in fabric
