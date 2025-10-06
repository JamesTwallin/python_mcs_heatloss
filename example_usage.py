"""Example usage of MCS Heat Pump Calculator."""
from mcs_calculator import HeatPumpCalculator
from mcs_calculator.room import Wall, Window, Floor
import json


def example_simple_bungalow():
    """Example: Simple bungalow heat loss calculation."""
    print("=" * 80)
    print("EXAMPLE: Simple Bungalow in Manchester (M Postcode)")
    print("=" * 80)

    # Initialize calculator for Manchester
    calc = HeatPumpCalculator(postcode_area='M', building_category='B')

    # Display location info
    location = calc.get_location_info()
    print(f"\nLocation Information:")
    print(f"  Postcode Area: {location['postcode_area']}")
    print(f"  Location: {location['location']}")
    print(f"  Design External Temperature: {location['design_external_temp']}°C")
    print(f"  Degree Days: {location['degree_days']}")

    # Create building
    building = calc.create_building('Manchester Bungalow')

    # Living Room
    living_room = calc.create_room(
        name='Living Room',
        room_type='Lounge',
        floor_area=25.0,
        height=2.4
    )
    living_room.walls.append(Wall('External Wall 1', area=12.0, u_value=0.3))
    living_room.walls.append(Wall('External Wall 2', area=9.6, u_value=0.3))
    living_room.windows.append(Window('Window 1', area=3.0, u_value=1.4))
    living_room.windows.append(Window('Window 2', area=2.0, u_value=1.4))
    living_room.floors.append(Floor('Ground Floor', area=25.0, u_value=0.25, temperature_factor=0.5))
    living_room.thermal_bridging_factor = 0.15
    building.add_room(living_room)

    # Kitchen/Dining
    kitchen = calc.create_room(
        name='Kitchen/Dining',
        room_type='Kitchen',
        floor_area=20.0,
        height=2.4
    )
    kitchen.walls.append(Wall('External Wall', area=16.8, u_value=0.3))
    kitchen.windows.append(Window('Window', area=2.5, u_value=1.4))
    kitchen.floors.append(Floor('Ground Floor', area=20.0, u_value=0.25, temperature_factor=0.5))
    kitchen.thermal_bridging_factor = 0.15
    building.add_room(kitchen)

    # Bedroom 1
    bedroom1 = calc.create_room(
        name='Bedroom 1',
        room_type='Bedroom',
        floor_area=15.0,
        height=2.4
    )
    bedroom1.walls.append(Wall('External Wall', area=12.0, u_value=0.3))
    bedroom1.windows.append(Window('Window', area=2.0, u_value=1.4))
    bedroom1.floors.append(Floor('Ground Floor', area=15.0, u_value=0.25, temperature_factor=0.5))
    bedroom1.thermal_bridging_factor = 0.15
    building.add_room(bedroom1)

    # Bedroom 2
    bedroom2 = calc.create_room(
        name='Bedroom 2',
        room_type='Bedroom',
        floor_area=12.0,
        height=2.4
    )
    bedroom2.walls.append(Wall('External Wall', area=9.6, u_value=0.3))
    bedroom2.windows.append(Window('Window', area=1.5, u_value=1.4))
    bedroom2.floors.append(Floor('Ground Floor', area=12.0, u_value=0.25, temperature_factor=0.5))
    bedroom2.thermal_bridging_factor = 0.15
    building.add_room(bedroom2)

    # Bathroom
    bathroom = calc.create_room(
        name='Bathroom',
        room_type='Bathroom',
        floor_area=6.0,
        height=2.4
    )
    bathroom.walls.append(Wall('External Wall', area=7.2, u_value=0.3))
    bathroom.windows.append(Window('Window', area=0.8, u_value=1.4))
    bathroom.floors.append(Floor('Ground Floor', area=6.0, u_value=0.25, temperature_factor=0.5))
    bathroom.thermal_bridging_factor = 0.15
    building.add_room(bathroom)

    # Hall
    hall = calc.create_room(
        name='Hall',
        room_type='Hall',
        floor_area=8.0,
        height=2.4
    )
    hall.floors.append(Floor('Ground Floor', area=8.0, u_value=0.25, temperature_factor=0.5))
    hall.thermal_bridging_factor = 0.15
    building.add_room(hall)

    # Calculate heat loss
    print("\n" + "=" * 80)
    print("HEAT LOSS CALCULATION")
    print("=" * 80)

    summary = calc.calculate_building_heat_loss()

    print(f"\nBuilding: {summary['building_name']}")
    print(f"Number of Rooms: {summary['num_rooms']}")
    print(f"\nDesign Conditions:")
    print(f"  External Temperature: {summary['external_temp']}°C")
    print(f"  Degree Days: {summary['degree_days']}")

    print(f"\nRoom-by-Room Heat Loss:")
    print(f"{'Room':<20} {'Temp':>6} {'Fabric W':>10} {'Vent W':>10} {'Total W':>10} {'Annual kWh':>12}")
    print("-" * 80)

    for room in summary['rooms']:
        print(f"{room['room_name']:<20} "
              f"{room['design_temp']:>6.1f} "
              f"{room['fabric_loss']['watts']['total']:>10.0f} "
              f"{room['ventilation_loss']['watts']:>10.0f} "
              f"{room['total_loss']['watts']:>10.0f} "
              f"{room['total_loss']['kwh']:>12.0f}")

    print("-" * 80)
    print(f"{'TOTAL':<20} {'':<6} {'':<10} {'':<10} "
          f"{summary['total_heat_loss']['watts']:>10.0f} "
          f"{summary['total_heat_loss']['kwh']:>12.0f}")

    # Hot water calculation
    print("\n" + "=" * 80)
    print("HOT WATER ENERGY CALCULATION")
    print("=" * 80)

    hw_energy = calc.calculate_hot_water_energy(
        num_occupants=4,
        daily_usage_litres=200,
        cold_water_temp=10,
        hot_water_temp=60
    )

    print(f"\nOccupants: {4}")
    print(f"Daily Usage: {hw_energy['daily_usage_litres']} litres at {hw_energy['hot_water_temp']}°C")
    print(f"Cold Water Temperature: {hw_energy['cold_water_temp']}°C")
    print(f"Daily Energy Requirement: {hw_energy['daily_energy_kwh']:.1f} kWh/day")
    print(f"Annual Energy Requirement: {hw_energy['annual_energy_kwh']:.0f} kWh/year")

    # Heat pump sizing
    print("\n" + "=" * 80)
    print("HEAT PUMP SIZING")
    print("=" * 80)

    design_heat_loss_kw = summary['total_heat_loss']['watts'] / 1000
    hot_water_peak_kw = 3.0  # Typical for domestic DHW cylinder reheat

    sizing = calc.size_heat_pump(
        design_heat_loss_kw=design_heat_loss_kw,
        hot_water_demand_kw=hot_water_peak_kw,
        oversizing_factor=1.0
    )

    print(f"\nDesign Heat Loss: {sizing['design_heat_loss_kw']:.2f} kW")
    print(f"Hot Water Demand: {sizing['hot_water_demand_kw']:.2f} kW")
    print(f"Oversizing Factor: {sizing['oversizing_factor']:.1f}")
    print(f"\nRequired Heat Pump Capacity: {sizing['required_capacity_kw']:.2f} kW")

    # Annual energy consumption
    print("\n" + "=" * 80)
    print("ANNUAL ENERGY CONSUMPTION")
    print("=" * 80)

    # Assume different COP values
    for cop in [2.5, 3.0, 3.5, 4.0]:
        annual_energy = calc.calculate_annual_energy_consumption(
            space_heating_kwh=summary['total_heat_loss']['kwh'],
            hot_water_kwh=hw_energy['annual_energy_kwh'],
            cop=cop
        )

        print(f"\nHeat Pump COP: {cop}")
        print(f"  Space Heating Demand: {annual_energy['space_heating_demand_kwh']:,.0f} kWh/year")
        print(f"  Hot Water Demand: {annual_energy['hot_water_demand_kwh']:,.0f} kWh/year")
        print(f"  Total Heat Demand: {annual_energy['total_heat_demand_kwh']:,.0f} kWh/year")
        print(f"  Electricity Consumption: {annual_energy['electricity_consumption_kwh']:,.0f} kWh/year")

        # Estimate costs (example rates)
        electricity_rate = 0.30  # £/kWh
        annual_cost = annual_energy['electricity_consumption_kwh'] * electricity_rate
        print(f"  Estimated Annual Cost (@ £{electricity_rate}/kWh): £{annual_cost:,.0f}")

    # Radiator sizing example
    print("\n" + "=" * 80)
    print("RADIATOR SIZING (for low temperature system)")
    print("=" * 80)

    print(f"\n{'Room':<20} {'Heat Loss':>12} {'Required Output':>18} {'Sizing Factor':>15}")
    print(f"{'':20} {'(W)':>12} {'@ ΔT=50°C (W)':>18} {'':>15}")
    print("-" * 80)

    for room in summary['rooms']:
        rad_sizing = calc.calculate_radiator_sizing(
            room_heat_loss_w=room['total_loss']['watts'],
            room_temp=room['design_temp'],
            flow_temp=45,
            return_temp=40
        )

        print(f"{room['room_name']:<20} "
              f"{rad_sizing['room_heat_loss_w']:>12.0f} "
              f"{rad_sizing['required_output_at_delta_t_50']:>18.0f} "
              f"{rad_sizing['sizing_factor']:>15.2f}x")

    print("\nNote: Radiators need to be larger for low temperature heat pump systems")
    print("      compared to traditional high temperature boiler systems.")

    # Save summary to JSON
    output_file = 'heat_loss_summary.json'
    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"\n\nFull summary saved to: {output_file}")


if __name__ == '__main__':
    example_simple_bungalow()
