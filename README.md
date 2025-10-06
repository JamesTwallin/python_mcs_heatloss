# MCS Heat Pump Calculator - Python Implementation

A Python implementation of the MCS (Microgeneration Certification Scheme) Heat Pump Calculator for heat loss calculations and heat pump system design, based on BS EN 12831.

## Features

- **Heat Loss Calculation**: Room-by-room and whole building heat loss calculations following BS EN 12831
- **Degree Days Data**: Built-in CIBSE degree days data for all UK postcode areas
- **Hot Water Energy**: Calculate domestic hot water energy requirements
- **Heat Pump Sizing**: Size heat pumps based on design heat loss and hot water demand
- **Radiator Sizing**: Calculate radiator sizing for low-temperature heat pump systems
- **Annual Energy Consumption**: Estimate annual energy consumption and costs
- **U-Value Calculations**: Floor U-value calculations for solid and suspended floors

## Installation

### Using Conda (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd python_mcs_heatloss

# Create and activate conda environment
conda create -n python_mcs_heatloss python=3.12
conda activate python_mcs_heatloss

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/test_calculator.py -v

# Run example
python example_usage.py
```

### Using pip

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from mcs_calculator import HeatPumpCalculator
from mcs_calculator import Wall, Window, Floor

# Initialize calculator for Manchester (M postcode)
calc = HeatPumpCalculator(postcode_area='M', building_category='B')

# Create building
building = calc.create_building('My House')

# Create a room
living_room = calc.create_room(
    name='Living Room',
    room_type='Lounge',
    floor_area=25.0,
    height=2.4
)

# Add fabric elements
living_room.walls.append(Wall('External Wall', area=15, u_value=0.3))
living_room.windows.append(Window('Window', area=4, u_value=1.4))
living_room.floors.append(Floor('Ground Floor', area=25, u_value=0.25))
living_room.thermal_bridging_factor = 0.15

building.add_room(living_room)

# Calculate heat loss
summary = calc.calculate_building_heat_loss()

print(f"Total Heat Loss: {summary['total_heat_loss']['watts']:.0f} W")
print(f"Annual Energy: {summary['total_heat_loss']['kwh']:.0f} kWh")
```

## Module Structure

```
mcs_calculator/
├── __init__.py          # Package initialization
├── calculator.py        # Main HeatPumpCalculator class
├── room.py             # Room, Building, Wall, Window, Floor classes
└── data_tables.py      # Lookup tables (degree days, U-values, etc.)

tests/
└── test_calculator.py   # Comprehensive test suite

example_usage.py         # Complete example with detailed output
```

## Core Classes

### HeatPumpCalculator

Main calculator class for heat pump system design.

```python
calc = HeatPumpCalculator(postcode_area='SW', building_category='B')

# Get location information
location = calc.get_location_info()

# Create building and rooms
building = calc.create_building('House Name')
room = calc.create_room('Living Room', 'Lounge', floor_area=25)

# Calculate heat loss
summary = calc.calculate_building_heat_loss()

# Hot water energy
hw_energy = calc.calculate_hot_water_energy(num_occupants=4)

# Size heat pump
sizing = calc.size_heat_pump(design_heat_loss_kw=5.0, hot_water_demand_kw=3.0)

# Annual energy consumption
energy = calc.calculate_annual_energy_consumption(
    space_heating_kwh=10000,
    hot_water_kwh=4000,
    cop=3.5
)

# Radiator sizing
rad_sizing = calc.calculate_radiator_sizing(
    room_heat_loss_w=1500,
    room_temp=21,
    flow_temp=45,
    return_temp=40
)
```

### Room

Represents a room with fabric elements and calculates heat loss.

```python
from mcs_calculator import Room, Wall, Window, Floor

room = Room(
    name='Bedroom',
    room_type='Bedroom',
    design_temp=18,
    volume=36,
    air_change_rate=1.0,
    thermal_bridging_factor=0.15
)

# Add fabric elements
room.walls.append(Wall('Wall', area=12, u_value=0.3))
room.windows.append(Window('Window', area=2, u_value=1.4))
room.floors.append(Floor('Floor', area=15, u_value=0.25, temperature_factor=0.5))

# Calculate heat loss
external_temp = -2.0
degree_days = 2033

fabric_loss = room.fabric_heat_loss_watts(external_temp)
vent_loss = room.ventilation_heat_loss_watts(external_temp)
total_loss = room.total_heat_loss_watts(external_temp)
annual_kwh = room.total_heat_loss_kwh(external_temp, degree_days)
```

### Data Tables

Built-in lookup tables for UK-specific data.

```python
from mcs_calculator import DegreeDays, RoomTemperatures, VentilationRates, FloorUValues

# Degree days
degree_days = DegreeDays.get_degree_days('M')  # Manchester
design_temp = DegreeDays.get_design_temp('M')
location = DegreeDays.get_location('M')

# Room temperatures
temp = RoomTemperatures.get_temperature('Lounge')  # 21°C

# Ventilation rates
ach = VentilationRates.get_rate('Kitchen', category='B')  # 1.5 ACH

# Floor U-values
u_value = FloorUValues.calculate_floor_u_value(
    floor_type='solid',
    perimeter=20,
    area=25,
    insulation_thickness=0.1
)
```

## Heat Loss Calculation Methodology

The calculator follows BS EN 12831 for heat loss calculations:

### Fabric Heat Loss

```
Q_fabric = Σ (A × U × ΔT × f)
```

Where:
- A = area (m²)
- U = U-value (W/m²K)
- ΔT = temperature difference (K)
- f = temperature correction factor (e.g., 0.5 for ground floors)

### Ventilation Heat Loss

```
Q_ventilation = 0.33 × n × V × ΔT
```

Where:
- 0.33 = specific heat capacity of air (Wh/m³K)
- n = air change rate (ACH)
- V = volume (m³)
- ΔT = temperature difference (K)

### Thermal Bridging

Additional 15% (typical for post-2006 buildings) added to fabric heat loss to account for thermal bridges.

### Annual Energy

```
kWh = Q × DD × 24 / 1000
```

Where:
- Q = heat loss per degree (W/K)
- DD = degree days
- 24 = hours per day

## Room Types and Default Values

| Room Type    | Design Temp (°C) | Ventilation (ACH) |
|--------------|------------------|-------------------|
| Lounge       | 21               | 1.0 (Category B)  |
| Dining       | 21               | 1.0               |
| Bedroom      | 18               | 1.0               |
| Kitchen      | 18               | 1.5               |
| Bathroom     | 22               | 1.5               |
| Hall/Landing | 18               | 1.0               |

Building Categories:
- **Category A**: Higher ventilation (older/leakier buildings)
- **Category B**: Medium ventilation (standard)
- **Category C**: Lower ventilation (very tight/new buildings)

## Example Output

```
HEAT LOSS CALCULATION
================================================================================

Room                   Temp   Fabric W     Vent W    Total W   Annual kWh
--------------------------------------------------------------------------------
Living Room            21.0        460        477        937         2124
Kitchen/Dining         18.0        268        501        769         1990
Bedroom 1              18.0        201        251        451         1168
--------------------------------------------------------------------------------
TOTAL                                                   2969         7259

HEAT PUMP SIZING
Required Heat Pump Capacity: 5.97 kW

ANNUAL ENERGY CONSUMPTION (COP = 3.5)
  Space Heating Demand: 7,259 kWh/year
  Hot Water Demand: 4,245 kWh/year
  Total Heat Demand: 11,504 kWh/year
  Electricity Consumption: 3,287 kWh/year
  Estimated Annual Cost (@ £0.30/kWh): £986
```

## Testing

The package includes comprehensive tests:

```bash
# Run all tests
pytest tests/test_calculator.py -v

# Run specific test class
pytest tests/test_calculator.py::TestRoom -v

# Run with coverage
pytest tests/test_calculator.py --cov=mcs_calculator
```

Test coverage includes:
- Degree days lookup
- Floor U-value calculations
- Room heat loss (fabric and ventilation)
- Thermal bridging
- Hot water energy
- Heat pump sizing
- Radiator sizing
- Complete building calculations

## Comparison with Excel Calculator

This Python implementation provides the same core functionality as the MCS Heat Pump Calculator Excel spreadsheet (Version 1.10), with the following advantages:

1. **Programmatic Access**: Integrate calculations into your own applications
2. **Batch Processing**: Calculate heat loss for multiple buildings efficiently
3. **Version Control**: Track changes to building designs over time
4. **Automation**: Automate repetitive calculations
5. **Testing**: Comprehensive test suite ensures accuracy
6. **Extensibility**: Easy to add custom calculations or modify existing ones

## Requirements

- Python 3.12+
- openpyxl >= 3.1.2 (for reading Excel files)
- pandas >= 2.0.0
- numpy >= 1.24.0
- pytest >= 7.4.0 (for testing)

## License

This is a Python implementation of publicly available MCS heat loss calculation methods following BS EN 12831.

## Contributing

Contributions are welcome! Please ensure:

1. All tests pass: `pytest tests/ -v`
2. Code follows PEP 8 style guidelines
3. New features include tests
4. Documentation is updated

## Support

For issues or questions, please open an issue on the GitHub repository.

## References

- BS EN 12831-1:2017 - Energy performance of buildings - Method for calculation of the design heat load
- CIBSE Guide A - Environmental Design
- MCS Installation Standard MIS 3005
- MCS Heat Pump Calculator (Excel) Version 1.10

## Version History

### Version 1.0.0 (2025-10-06)
- Initial Python implementation
- Complete heat loss calculation engine
- Comprehensive test suite
- Example usage scripts
- Full documentation
