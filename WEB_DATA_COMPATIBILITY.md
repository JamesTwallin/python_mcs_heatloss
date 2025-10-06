# Web Interface Data Compatibility

## Overview

The web interface (3D visualization) and Python calculator share the same JSON data format with 100% compatibility. The web interface adds optional visualization fields that are safely ignored by the Python calculator.

## Data Flow

```
Web Interface ──> JSON ──> Python Calculator
              <──        <──
```

Both systems can read and write the same JSON files without data loss.

## Core Fields (Used by Both)

These fields are used by both the Python calculator and web interface:

### Room
- `name` (str): Room identifier
- `room_type` (str): Room type (Lounge, Bedroom, etc.)
- `design_temp` (float): Design temperature in °C
- `air_change_rate` (float): Air changes per hour
- `thermal_bridging` (float): Thermal bridging percentage (e.g., 15 for 15%)
- `walls` (list): Wall elements
- `windows` (list): Window elements
- `floors` (list): Floor elements

### Wall
- `name` (str): Wall identifier
- `area` (float): Area in m²
- `u_value` (float): U-value in W/m²K
- `boundary` (str): 'external', 'ground', 'unheated', or adjacent room name
- `temperature_factor` (float): Temperature correction factor (0-1)

### Window
- `name` (str): Window identifier
- `area` (float): Area in m²
- `u_value` (float): U-value in W/m²K

### Floor
- `name` (str): Floor identifier
- `area` (float): Area in m²
- `u_value` (float): U-value in W/m²K
- `temperature_factor` (float): Ground contact factor (typically 0.5)

## Visualization-Only Fields (Web Interface Only)

These fields are added by the web interface for 3D positioning and are **ignored** by the Python calculator:

### Room
- `position_x` (float): X position in 3D space (meters)
- `position_z` (float): Z position in 3D space (meters)
- `width` (float): Room width in meters (for 3D visualization)
- `depth` (float): Room depth in meters (for 3D visualization)
- `height` (float): Room height in meters (for 3D visualization)

### Window
- `wall` (str): Which wall the window is on ('front', 'back', 'left', 'right')

## Python Calculator Compatibility

The Python calculator uses **kwargs and optional dataclass fields, so it automatically ignores any extra fields in the JSON. This means:

1. ✅ JSON exported from web interface can be loaded in Python
2. ✅ JSON exported from Python can be loaded in web interface
3. ✅ No data loss when round-tripping between systems
4. ✅ New visualization fields won't break Python calculations

## Example JSON

```json
{
  "building_name": "My House",
  "postcode_area": "M",
  "building_category": "B",
  "external_temp": -3.1,
  "rooms": [
    {
      "name": "Lounge",
      "room_type": "Lounge",
      "width": 5.0,          // Web only
      "depth": 4.0,          // Web only
      "height": 2.4,
      "design_temp": 21.0,
      "position_x": 0.0,     // Web only
      "position_z": 0.0,     // Web only
      "air_change_rate": 0.8,
      "thermal_bridging": 15,
      "walls": [
        {
          "name": "North Wall",
          "area": 12.0,
          "u_value": 0.3,
          "boundary": "external",
          "temperature_factor": 1.0
        },
        {
          "name": "Party Wall",
          "area": 12.0,
          "u_value": 0.5,
          "boundary": "Kitchen",  // Inter-room heat transfer
          "temperature_factor": 1.0
        }
      ],
      "windows": [
        {
          "name": "Front Window",
          "area": 4.0,
          "u_value": 1.4,
          "wall": "front"        // Web only
        }
      ],
      "floors": [
        {
          "name": "Ground Floor",
          "area": 20.0,
          "u_value": 0.25,
          "temperature_factor": 0.5
        }
      ]
    }
  ]
}
```

## Calculation Logic Flow

Both systems use the **exact same formulas** from BS EN 12831:

### Fabric Heat Loss
```
Q_fabric = Σ(A × U × ΔT × f)
```

For inter-room walls:
```
Q_inter_room = A × U × (T_room - T_adjacent)
```

### Ventilation Heat Loss
```
Q_vent = 0.33 × ACH × V × ΔT
```

### Total
```
Q_total = (Q_fabric + Q_inter_room) × (1 + thermal_bridging) + Q_vent
```

The web interface implements these calculations in JavaScript, mirroring the Python code exactly.

## Testing Compatibility

To verify compatibility:

1. Export JSON from web interface
2. Load in Python calculator
3. Run calculations in both
4. Results should match exactly (within floating-point precision)

Example test:
```python
# Python
from mcs_calculator import HeatPumpCalculator
import json

with open('building.json') as f:
    data = json.load(f)

calc = HeatPumpCalculator(postcode_area=data['postcode_area'])
building = calc.building
# Load rooms from data...
summary = calc.calculate_building_heat_loss()
print(f"Python: {summary['total_heat_loss_watts']}W")
```

```javascript
// Web
const result = calculateHeatLoss();
console.log(`Web: ${result.total_watts}W`);
```

Both should produce identical results.

## Version Compatibility

- Python calculator: Core fields only, ignores extras
- Web interface: Reads all fields, adds visualization fields when saving

This design ensures **forward and backward compatibility** between versions.
