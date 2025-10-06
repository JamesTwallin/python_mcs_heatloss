"""Data tables and lookup functions for MCS Heat Pump Calculator."""
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class DegreeDayData:
    """Degree day data for a postcode area."""
    postcode_area: str
    cibse_temp: float
    degree_days: float
    weeks_52: float
    weeks_39: float
    weeks_39_normalized: float
    location: Optional[str] = None

    def __post_init__(self):
        """Calculate derived values."""
        if self.weeks_52 == 0:
            self.weeks_52 = self.degree_days / 41.046
        if self.weeks_39 == 0:
            self.weeks_39 = self.degree_days * 0.95
        if self.weeks_39_normalized == 0:
            self.weeks_39_normalized = self.weeks_39 / 41.046


class DegreeDays:
    """Degree days lookup table based on CIBSE Guide A."""

    # Data from "Post Code Degree Days" sheet
    DATA = {
        'AB': {'temp': -4.2, 'degree_days': 2668, 'location': 'NE Scotland (Dyce)'},
        'AL': {'temp': -2.0, 'degree_days': 2033, 'location': 'Thames Valley (Heathrow)'},
        'B': {'temp': -3.3, 'degree_days': 2265, 'location': 'Severn Valley (Birmingham)'},
        'BA': {'temp': -2.5, 'degree_days': 2025, 'location': 'South Western (Yeovilton)'},
        'BB': {'temp': -3.1, 'degree_days': 2317, 'location': 'North Western (Squires Gate)'},
        'BD': {'temp': -3.6, 'degree_days': 2252, 'location': 'Pennines (Leeds)'},
        'BH': {'temp': -1.7, 'degree_days': 1908, 'location': 'South Western (Hurn)'},
        'BL': {'temp': -3.1, 'degree_days': 2317, 'location': 'North Western (Squires Gate)'},
        'BN': {'temp': -2.0, 'degree_days': 1830, 'location': 'South Eastern (Gatwick)'},
        'BR': {'temp': -2.0, 'degree_days': 2033, 'location': 'Thames Valley (Heathrow)'},
        'BS': {'temp': -2.5, 'degree_days': 2025, 'location': 'South Western (Yeovilton)'},
        'BT': {'temp': -3.5, 'degree_days': 2414, 'location': 'Northern Ireland (Aldergrove)'},
        'CA': {'temp': -3.2, 'degree_days': 2378, 'location': 'Borders (Carlisle)'},
        'CB': {'temp': -2.9, 'degree_days': 2163, 'location': 'East Anglia (Cambridge)'},
        'CF': {'temp': -2.5, 'degree_days': 2058, 'location': 'South Wales (Rhoose)'},
        'CH': {'temp': -2.6, 'degree_days': 2176, 'location': 'North Western (Hawarden)'},
        'CM': {'temp': -2.0, 'degree_days': 2033, 'location': 'Thames Valley (Heathrow)'},
        'CO': {'temp': -2.0, 'degree_days': 2033, 'location': 'Thames Valley (Heathrow)'},
        'CR': {'temp': -2.0, 'degree_days': 2033, 'location': 'Thames Valley (Heathrow)'},
        'CT': {'temp': -1.7, 'degree_days': 1893, 'location': 'South Eastern (Manston)'},
        'CV': {'temp': -3.3, 'degree_days': 2265, 'location': 'Severn Valley (Birmingham)'},
        'CW': {'temp': -2.6, 'degree_days': 2176, 'location': 'North Western (Hawarden)'},
        'DA': {'temp': -2.0, 'degree_days': 2033, 'location': 'Thames Valley (Heathrow)'},
        'DD': {'temp': -3.5, 'degree_days': 2363, 'location': 'East Scotland (Leuchars)'},
        'DE': {'temp': -3.3, 'degree_days': 2265, 'location': 'Severn Valley (Birmingham)'},
        'DG': {'temp': -3.3, 'degree_days': 2401, 'location': 'West Scotland (West Freugh)'},
        'DH': {'temp': -3.3, 'degree_days': 2273, 'location': 'Borders (Durham)'},
        'DL': {'temp': -3.3, 'degree_days': 2273, 'location': 'Borders (Durham)'},
        'DN': {'temp': -2.9, 'degree_days': 2325, 'location': 'East Pennines (Finningley)'},
        'DT': {'temp': -1.7, 'degree_days': 1908, 'location': 'South Western (Hurn)'},
        'DY': {'temp': -3.3, 'degree_days': 2265, 'location': 'Severn Valley (Birmingham)'},
        'E': {'temp': -2.0, 'degree_days': 2033, 'location': 'Thames Valley (Heathrow)'},
        'EC': {'temp': -2.0, 'degree_days': 2033, 'location': 'Thames Valley (Heathrow)'},
        'EH': {'temp': -3.2, 'degree_days': 2332, 'location': 'East Scotland (Turnhouse)'},
        'EN': {'temp': -2.0, 'degree_days': 2033, 'location': 'Thames Valley (Heathrow)'},
        'EX': {'temp': -2.3, 'degree_days': 1870, 'location': 'South Western (Exeter)'},
        'FK': {'temp': -3.2, 'degree_days': 2332, 'location': 'East Scotland (Turnhouse)'},
        'FY': {'temp': -3.1, 'degree_days': 2317, 'location': 'North Western (Squires Gate)'},
        'G': {'temp': -3.3, 'degree_days': 2401, 'location': 'West Scotland (West Freugh)'},
        'GL': {'temp': -2.8, 'degree_days': 2123, 'location': 'Severn Valley (Staverton)'},
        'GU': {'temp': -2.0, 'degree_days': 1830, 'location': 'South Eastern (Gatwick)'},
        'HA': {'temp': -2.0, 'degree_days': 2033, 'location': 'Thames Valley (Heathrow)'},
        'HD': {'temp': -3.6, 'degree_days': 2252, 'location': 'Pennines (Leeds)'},
        'HG': {'temp': -3.6, 'degree_days': 2252, 'location': 'Pennines (Leeds)'},
        'HP': {'temp': -2.4, 'degree_days': 2059, 'location': 'Midlands (Cranfield)'},
        'HR': {'temp': -2.9, 'degree_days': 2168, 'location': 'Wales (Shawbury)'},
        'HS': {'temp': -1.9, 'degree_days': 2668, 'location': 'NW Scotland (Stornoway)'},
        'HU': {'temp': -2.2, 'degree_days': 2257, 'location': 'East Pennines (Brough)'},
        'HX': {'temp': -3.6, 'degree_days': 2252, 'location': 'Pennines (Leeds)'},
        'IG': {'temp': -2.0, 'degree_days': 2033, 'location': 'Thames Valley (Heathrow)'},
        'IP': {'temp': -2.3, 'degree_days': 2081, 'location': 'East Anglia (Wattisham)'},
        'IV': {'temp': -4.2, 'degree_days': 2668, 'location': 'NE Scotland (Dyce)'},
        'KA': {'temp': -3.3, 'degree_days': 2401, 'location': 'West Scotland (West Freugh)'},
        'KT': {'temp': -2.0, 'degree_days': 2033, 'location': 'Thames Valley (Heathrow)'},
        'KW': {'temp': -3.6, 'degree_days': 2588, 'location': 'NE Scotland (Wick)'},
        'KY': {'temp': -3.5, 'degree_days': 2363, 'location': 'East Scotland (Leuchars)'},
        'L': {'temp': -2.6, 'degree_days': 2176, 'location': 'North Western (Hawarden)'},
        'LA': {'temp': -3.1, 'degree_days': 2317, 'location': 'North Western (Squires Gate)'},
        'LD': {'temp': -2.9, 'degree_days': 2168, 'location': 'Wales (Shawbury)'},
        'LE': {'temp': -3.3, 'degree_days': 2265, 'location': 'Severn Valley (Birmingham)'},
        'LL': {'temp': -2.6, 'degree_days': 2271, 'location': 'North Wales (Valley)'},
        'LN': {'temp': -2.7, 'degree_days': 2255, 'location': 'East Pennines (Cranwell)'},
        'LS': {'temp': -3.6, 'degree_days': 2252, 'location': 'Pennines (Leeds)'},
        'LU': {'temp': -2.4, 'degree_days': 2059, 'location': 'Midlands (Cranfield)'},
        'M': {'temp': -3.1, 'degree_days': 2275, 'location': 'North Western (Ringway)'},
        'ME': {'temp': -2.0, 'degree_days': 2033, 'location': 'Thames Valley (Heathrow)'},
        'MK': {'temp': -2.4, 'degree_days': 2059, 'location': 'Midlands (Cranfield)'},
        'ML': {'temp': -3.2, 'degree_days': 2332, 'location': 'East Scotland (Turnhouse)'},
        'N': {'temp': -2.0, 'degree_days': 2033, 'location': 'Thames Valley (Heathrow)'},
        'NE': {'temp': -3.3, 'degree_days': 2273, 'location': 'Borders (Durham)'},
        'NG': {'temp': -2.9, 'degree_days': 2217, 'location': 'East Midlands (Watnall)'},
        'NN': {'temp': -2.4, 'degree_days': 2059, 'location': 'Midlands (Cranfield)'},
        'NP': {'temp': -2.5, 'degree_days': 2058, 'location': 'South Wales (Rhoose)'},
        'NR': {'temp': -2.7, 'degree_days': 2174, 'location': 'East Anglia (Norwich)'},
        'NW': {'temp': -2.0, 'degree_days': 2033, 'location': 'Thames Valley (Heathrow)'},
        'OL': {'temp': -3.1, 'degree_days': 2275, 'location': 'North Western (Ringway)'},
        'OX': {'temp': -2.8, 'degree_days': 2022, 'location': 'Thames Valley (Benson)'},
        'PA': {'temp': -3.3, 'degree_days': 2401, 'location': 'West Scotland (West Freugh)'},
        'PE': {'temp': -2.7, 'degree_days': 2255, 'location': 'East Pennines (Cranwell)'},
        'PH': {'temp': -3.5, 'degree_days': 2363, 'location': 'East Scotland (Leuchars)'},
        'PL': {'temp': -2.2, 'degree_days': 1731, 'location': 'South Western (Plymouth)'},
        'PO': {'temp': -1.8, 'degree_days': 1909, 'location': 'South Coast (Thorney Island)'},
        'PR': {'temp': -3.1, 'degree_days': 2317, 'location': 'North Western (Squires Gate)'},
        'RG': {'temp': -2.0, 'degree_days': 2033, 'location': 'Thames Valley (Heathrow)'},
        'RH': {'temp': -2.0, 'degree_days': 1830, 'location': 'South Eastern (Gatwick)'},
        'RM': {'temp': -2.0, 'degree_days': 2033, 'location': 'Thames Valley (Heathrow)'},
        'S': {'temp': -3.2, 'degree_days': 2260, 'location': 'Pennines (Sheffield)'},
        'SA': {'temp': -2.3, 'degree_days': 1969, 'location': 'South Wales (Aberporth)'},
        'SE': {'temp': -2.0, 'degree_days': 2033, 'location': 'Thames Valley (Heathrow)'},
        'SG': {'temp': -2.4, 'degree_days': 2059, 'location': 'Midlands (Cranfield)'},
        'SK': {'temp': -3.1, 'degree_days': 2275, 'location': 'North Western (Ringway)'},
        'SL': {'temp': -2.0, 'degree_days': 2033, 'location': 'Thames Valley (Heathrow)'},
        'SM': {'temp': -2.0, 'degree_days': 2033, 'location': 'Thames Valley (Heathrow)'},
        'SN': {'temp': -2.8, 'degree_days': 2123, 'location': 'Severn Valley (Staverton)'},
        'SO': {'temp': -1.8, 'degree_days': 1909, 'location': 'South Coast (Thorney Island)'},
        'SP': {'temp': -2.8, 'degree_days': 2022, 'location': 'Thames Valley (Benson)'},
        'SR': {'temp': -3.3, 'degree_days': 2273, 'location': 'Borders (Durham)'},
        'SS': {'temp': -2.0, 'degree_days': 2033, 'location': 'Thames Valley (Heathrow)'},
        'ST': {'temp': -3.1, 'degree_days': 2275, 'location': 'North Western (Ringway)'},
        'SW': {'temp': -2.0, 'degree_days': 2033, 'location': 'Thames Valley (Heathrow)'},
        'SY': {'temp': -2.9, 'degree_days': 2168, 'location': 'Wales (Shawbury)'},
        'TA': {'temp': -2.5, 'degree_days': 2025, 'location': 'South Western (Yeovilton)'},
        'TD': {'temp': -3.2, 'degree_days': 2378, 'location': 'Borders (Carlisle)'},
        'TF': {'temp': -2.9, 'degree_days': 2168, 'location': 'Wales (Shawbury)'},
        'TN': {'temp': -2.0, 'degree_days': 1830, 'location': 'South Eastern (Gatwick)'},
        'TQ': {'temp': -2.3, 'degree_days': 1870, 'location': 'South Western (Exeter)'},
        'TR': {'temp': -1.6, 'degree_days': 1608, 'location': 'South Western (Camborne)'},
        'TS': {'temp': -3.3, 'degree_days': 2273, 'location': 'Borders (Durham)'},
        'TW': {'temp': -2.0, 'degree_days': 2033, 'location': 'Thames Valley (Heathrow)'},
        'UB': {'temp': -2.0, 'degree_days': 2033, 'location': 'Thames Valley (Heathrow)'},
        'W': {'temp': -2.0, 'degree_days': 2033, 'location': 'Thames Valley (Heathrow)'},
        'WA': {'temp': -2.6, 'degree_days': 2176, 'location': 'North Western (Hawarden)'},
        'WC': {'temp': -2.0, 'degree_days': 2033, 'location': 'Thames Valley (Heathrow)'},
        'WD': {'temp': -2.0, 'degree_days': 2033, 'location': 'Thames Valley (Heathrow)'},
        'WF': {'temp': -3.6, 'degree_days': 2252, 'location': 'Pennines (Leeds)'},
        'WN': {'temp': -3.1, 'degree_days': 2317, 'location': 'North Western (Squires Gate)'},
        'WR': {'temp': -3.3, 'degree_days': 2265, 'location': 'Severn Valley (Birmingham)'},
        'WS': {'temp': -3.3, 'degree_days': 2265, 'location': 'Severn Valley (Birmingham)'},
        'WV': {'temp': -3.3, 'degree_days': 2265, 'location': 'Severn Valley (Birmingham)'},
        'YO': {'temp': -3.6, 'degree_days': 2252, 'location': 'Pennines (Leeds)'},
        'ZE': {'temp': -1.2, 'degree_days': 2584, 'location': 'Shetland (Lerwick)'},
    }

    @classmethod
    def get_degree_days(cls, postcode_area: str) -> Optional[float]:
        """Get degree days for a postcode area."""
        data = cls.DATA.get(postcode_area.upper())
        return data['degree_days'] if data else None

    @classmethod
    def get_design_temp(cls, postcode_area: str) -> Optional[float]:
        """Get design external temperature for a postcode area."""
        data = cls.DATA.get(postcode_area.upper())
        return data['temp'] if data else None

    @classmethod
    def get_location(cls, postcode_area: str) -> Optional[str]:
        """Get location name for a postcode area."""
        data = cls.DATA.get(postcode_area.upper())
        return data['location'] if data else None


class FloorUValues:
    """Floor U-value calculation based on BS EN 12831."""

    @staticmethod
    def calculate_floor_u_value(
        floor_type: str,
        perimeter: float,
        area: float,
        wall_thickness: float = 0.3,
        insulation_thickness: float = 0.0,
        insulation_conductivity: float = 0.035
    ) -> float:
        """
        Calculate floor U-value using BS EN 12831 method.

        Args:
            floor_type: 'solid' or 'suspended'
            perimeter: External perimeter of floor (m)
            area: Floor area (m²)
            wall_thickness: Wall thickness (m)
            insulation_thickness: Insulation thickness (m)
            insulation_conductivity: Thermal conductivity of insulation (W/mK)

        Returns:
            U-value (W/m²K)
        """
        # Characteristic dimension
        B = area / (0.5 * perimeter) if perimeter > 0 else 0

        # Ground thermal conductivity (typical value)
        lambda_g = 2.0  # W/mK for typical soil

        # Total equivalent thickness
        dt = wall_thickness + insulation_thickness * (lambda_g / insulation_conductivity)

        if B < 0.1:
            return 0.0

        # Calculate U-value based on characteristic dimension
        if floor_type.lower() == 'solid':
            if B <= 0.5:
                u_value = lambda_g / (0.457 * B + dt)
            else:
                u_value = (2 * lambda_g / (3.14 * B + dt)) * (1 + 0.5 * (dt / (dt + lambda_g)))
        else:  # suspended
            # Simplified calculation for suspended floors
            # Additional resistance due to air gap
            R_air = 0.18  # m²K/W
            R_total = dt / lambda_g + R_air
            u_value = 1 / R_total if R_total > 0 else 0

        return u_value


class RoomTemperatures:
    """Design room temperatures based on BS EN 12831 and MCS Heat Pump Calculator v1.10."""

    TEMPERATURES = {
        'Bath': 22,
        'Bathroom': 22,
        'Bed & Ensuite': 22,
        'Bed/Study': 18,
        'Bedroom': 18,
        'Bedsitting': 21,
        'Breakfast': 21,
        'Cloaks/WC': 18,
        'Conservatory': 18,
        'Dining': 21,
        'Dressing': 18,
        'En Suite': 22,
        'Family': 21,
        'Games': 18,
        'Hall': 18,
        'Internal': 18,
        'Kitchen': 18,
        'Landing': 18,
        'Living': 21,
        'Lounge': 21,
        'Shower': 22,
        'Store': 15,
        'Study': 18,
        'Toilet': 18,
        'Utility': 18,
        'WC': 18,
    }

    @classmethod
    def get_temperature(cls, room_type: str) -> float:
        """
        Get design temperature for a room type.

        Args:
            room_type: Room type name

        Returns:
            Design temperature in °C (default 21°C if not found)
        """
        return cls.TEMPERATURES.get(room_type, 21)


class VentilationRates:
    """Natural ventilation rates based on BS EN 12831 and MCS Heat Pump Calculator v1.10."""

    # Air changes per hour by room category (from Excel Design Details columns AA-AF)
    RATES = {
        'A': {  # Category A - higher ventilation (older/leakier buildings)
            'Bath': 3.0,
            'Bathroom': 3.0,  # Alias for Bath
            'Bed & Ensuite': 2.0,
            'Bed/Study': 1.5,
            'Bedroom': 1.0,
            'Bedsitting': 1.5,
            'Breakfast': 1.5,
            'Cloaks/WC': 2.0,
            'Dining': 1.5,
            'Dressing': 1.5,
            'Family': 2.0,
            'Games': 1.5,
            'Hall': 2.0,
            'Internal': 0.0,
            'Kitchen': 2.0,
            'Landing': 2.0,
            'Living': 1.5,
            'Lounge': 1.5,
            'Shower': 3.0,
            'Store': 1.0,
            'Study': 1.5,
            'Toilet': 3.0,
            'Utility': 3.0,
        },
        'B': {  # Category B - medium ventilation (standard buildings)
            'Bath': 1.5,
            'Bathroom': 1.5,  # Alias for Bath
            'Bed & Ensuite': 1.5,
            'Bed/Study': 1.5,
            'Bedroom': 1.0,
            'Bedsitting': 1.0,
            'Breakfast': 1.0,
            'Cloaks/WC': 1.5,
            'Dining': 1.0,
            'Dressing': 1.0,
            'Family': 1.5,
            'Games': 1.0,
            'Hall': 1.0,
            'Internal': 0.0,
            'Kitchen': 1.5,
            'Landing': 1.0,
            'Living': 1.0,
            'Lounge': 1.0,
            'Shower': 1.5,
            'Store': 0.5,
            'Study': 1.5,
            'Toilet': 1.5,
            'Utility': 2.0,
        },
        'C': {  # Category C - lower ventilation (tight/new buildings)
            'Bath': 1.5,
            'Bathroom': 1.5,  # Alias for Bath
            'Bed & Ensuite': 1.0,
            'Bed/Study': 0.5,
            'Bedroom': 0.5,
            'Bedsitting': 0.5,
            'Breakfast': 0.5,
            'Cloaks/WC': 1.5,
            'Dining': 0.5,
            'Dressing': 0.5,
            'Family': 1.5,
            'Games': 0.5,
            'Hall': 0.5,
            'Internal': 0.0,
            'Kitchen': 1.5,
            'Landing': 0.5,
            'Living': 0.5,
            'Lounge': 0.5,
            'Shower': 1.5,
            'Store': 0.5,
            'Study': 0.5,
            'Toilet': 1.5,
            'Utility': 0.5,
        }
    }

    @classmethod
    def get_rate(cls, room_type: str, category: str = 'B') -> float:
        """
        Get ventilation rate (ACH) for a room type and building category.

        Args:
            room_type: Room type name (e.g., 'Lounge', 'Kitchen', 'Bedroom')
            category: Building category 'A' (leaky), 'B' (standard), or 'C' (tight)

        Returns:
            Air changes per hour (ACH) for the room type
        """
        category_rates = cls.RATES.get(category, cls.RATES['B'])
        return category_rates.get(room_type, 1.0)
