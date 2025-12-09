from datetime import datetime
import gurobipy as gp
from gurobipy import Model, GRB
from Model.Flight import Flight
from Model.Ticket import Ticket
import os
import json


def load_settings():
    try:
        import QtDesigner
        import inspect

        package_file = inspect.getfile(QtDesigner)
        package_dir = os.path.dirname(os.path.abspath(package_file))

        settings_path = os.path.join(package_dir, 'settings.json')

        if os.path.exists(settings_path):
            with open(settings_path, 'r') as f:
                settings = json.load(f)
                print(f"Successfully loaded settings from: {settings_path}")
                return settings
        else:
            print(f"settings.json not found at: {settings_path}")

    except Exception as e:
        print(f"Error loading settings: {e}")

    return {}


def dynamic_ticket_price(ticket: Ticket):

    settings = load_settings()

    # Convert ALL string values to appropriate types
    FUEL_COST_Km = float(settings["fuel_cost"])
    advanced_booking_discount = float(settings["advanced_booking_discount"]) / 100  # Convert % to decimal
    holiday_factor = float(settings["holiday_factor"]) / 100
    late_booking = float(settings["late_booking"]) / 100
    luggage_surcharge = float(settings["luggage_surcharge"]) / 100  # Convert % to decimal
    stop_discount = float(settings["stop_discount"]) / 100
    weekend_surcharge = float(settings["weekend_surcharge"]) / 100
    roundtrip_discount = float(settings["roundtrip_discount"]) / 100
    student_discount = float(settings["student_discount"]) / 100
    tourist_surcharge = float(settings["tourist_surcharge"]) / 100
    base_price_value = float(settings["base_price"])

    # FIX: Convert efficiency factor to float
    efficiency_factor = float(settings["efficiency"])

    # Seat class factors
    first_class_factor = float(settings["first_class_factor"])
    business_factor = float(settings["business_factor"])
    premium_economy_factor = float(settings["premium_economy_factor"])
    economy_factor = float(settings.get("economy_factor", 1))

    # Cost factors
    extended_cost_factor = float(settings["extended_cost_factor"])
    long_cost_factor = float(settings["long_cost_factor"])
    narrow_cost_factor = float(settings["narrow_cost_factor"])
    ultra_cost_factor = float(settings["ultra_cost_factor"])

    # Special offers from JSON
    special_offers = settings.get("special_offers", [])

    m = Model("dynamic_ticket_pricing")
    m.Params.LogToConsole = 0  # Silence Gurobi output

    flight = ticket.flight
    airline = flight.airline
    aircraft = flight.aircraft


    # Main decision variable: Ticket price
    price = m.addVar(name="ticket_price", lb=0, vtype=GRB.CONTINUOUS)

    # Dynamic demand factor - calculated based on real factors
    demand_factor = m.addVar(name="demand_factor", lb=0.5, ub=3.0, vtype=GRB.CONTINUOUS)

    seat_factors = {
        "first": first_class_factor,
        "business": business_factor,
        "premium_economy": premium_economy_factor,
        "economic": economy_factor,
        "economy": economy_factor  # Add alias for economy
    }

    seat_factor = seat_factors.get(ticket.seat_type.lower().replace(" ", "_"), economy_factor)
    base_price = base_price_value * seat_factor

    # Aircraft operating cost: fuel + distance factor
    # Determine aircraft type cost factor
    # Check if aircraft is a dictionary or object
    if isinstance(aircraft, dict):
        aircraft_capacity = ticket.flight.max_seats
        aircraft_type = aircraft["name"]
    else:
        # It's an object, access attributes directly
        aircraft_capacity = ticket.flight.max_seats
        aircraft_type = aircraft
        if aircraft_type == 'narrow':
            aircraft_name = getattr(aircraft, 'name', '').lower()
            if 'wide' in aircraft_name:
                aircraft_type = 'wide'
            elif 'long' in aircraft_name or 'range' in aircraft_name:
                aircraft_type = 'long_range'
            elif 'ultra' in aircraft_name:
                aircraft_type = 'ultra_long_range'

    cost_factors = {
        "narrow": narrow_cost_factor,
        "wide": extended_cost_factor,
        "long_range": long_cost_factor,
        "ultra_long_range": ultra_cost_factor
    }
    aircraft_cost_factor = cost_factors.get(aircraft_type, narrow_cost_factor)

    aircraft_cost = aircraft_cost_factor * FUEL_COST_Km * flight.distance


    # 1. Load factor from sold seats
    if hasattr(flight, 'sold_seats') and aircraft_capacity > 0:
        load_factor = flight.sold_seats / aircraft_capacity
    else:
        load_factor = 0.5  # Default 50% load factor

    # 2. Holiday demand boost
    if hasattr(flight, 'is_holiday_period') and callable(flight.is_holiday_period):
        is_holiday = 1 if flight.is_holiday_period() else 0
    else:
        is_holiday = 0

    # 3. Tourist destination boost - FIXED: uses correct method name from Flight model
    if hasattr(flight, 'destiation_is_tourist_hotspot') and callable(flight.destiation_is_tourist_hotspot):
        is_tourist_destination = 1 if flight.destiation_is_tourist_hotspot() else 0
    else:
        is_tourist_destination = 0

    # 4. Weekend demand boost
    if hasattr(ticket, 'is_weekend') and callable(ticket.is_weekend):
        is_weekend = 1 if ticket.is_weekend() else 0
    else:
        is_weekend = 0

    # 5. Late booking penalty/reward
    if hasattr(ticket, 'is_advanced_booking') and callable(ticket.is_advanced_booking):
        is_late_booking = 1 if not ticket.is_advanced_booking() else 0
    else:
        is_late_booking = 0

    # 6. Check for stops
    if hasattr(flight, 'stops'):
        flight_stops = flight.stops
    elif hasattr(flight, 'determine_stops') and callable(flight.determine_stops):
        flight_stops = flight.determine_stops()
    else:
        flight_stops = 0


    special_discount_total = 0

    # Check if ticket has any special offers applied
    if hasattr(ticket, 'specialoffers'):
        for offer in ticket.specialoffers:
            # Check if this offer exists in settings.json
            for json_offer in special_offers:
                if json_offer["name"].lower() == offer.name.lower():
                    special_discount_total += float(json_offer["value"]) / 100

    # Apply student discount from settings if applicable
    if hasattr(ticket, 'is_student') and ticket.is_student:
        special_discount_total += student_discount

    # Advanced booking discount
    adv_discount = advanced_booking_discount if hasattr(ticket, 'is_advanced_booking') and callable(
        ticket.is_advanced_booking) and ticket.is_advanced_booking() else 0

    # Late booking surcharge
    late_surcharge = late_booking if is_late_booking else 0

    # Weekend surcharge
    weekend_surcharge_val = weekend_surcharge if is_weekend else 0

    # Holiday factor (if flight is during holiday period)
    holiday_surcharge = holiday_factor if is_holiday else 0

    # Luggage surcharge (if extra luggage)
    luggage_surcharge_val = luggage_surcharge if hasattr(ticket, 'extra_luggage') and ticket.extra_luggage else 0

    # Stop discount (if flight has stops)
    stop_discount_val = stop_discount if flight_stops > 0 else 0

    # Roundtrip discount (assuming roundtrip if return date exists)
    roundtrip_discount_val = roundtrip_discount if hasattr(flight, 'date_return') and flight.date_return else 0

    # Tourist surcharge (if destination is tourist hotspot)
    tourist_surcharge_val = tourist_surcharge if is_tourist_destination else 0

    # Demand factor is influenced by multiple real factors:
    # 1. Base demand: 1.0
    # 2. Load factor influence: +0.5 when fully loaded, +0 when empty
    # 3. Holiday boost: +0.3 during holidays
    # 4. Tourist destination boost: +0.2 for tourist spots
    # 5. Weekend boost: +0.15 on weekends
    # 6. Late booking penalty: -0.1 for late bookings

    base_demand = 1.0
    load_factor_influence = 0.5 * load_factor  # 0 to 0.5 based on load
    holiday_boost = 0.3 * is_holiday
    tourist_boost = 0.2 * is_tourist_destination
    weekend_boost = 0.15 * is_weekend
    late_penalty = -0.1 * is_late_booking

    # Calculate total demand factor
    total_demand = (
            base_demand +
            load_factor_influence +
            holiday_boost +
            tourist_boost +
            weekend_boost +
            late_penalty
    )

    # Constraint: Demand factor equals calculated total demand
    m.addConstr(demand_factor == total_demand, "demand_calculation")

    # -----------------------------
    # CONSTRAINTS
    # -----------------------------

    # Constraint 1: Expected price calculation - FIXED: Store as regular float, not expression
    expected_price_val = (
            base_price *
            (1 - adv_discount - special_discount_total - stop_discount_val - roundtrip_discount_val) *
            (1 + weekend_surcharge_val + holiday_surcharge + late_surcharge +
             luggage_surcharge_val + tourist_surcharge_val) *
            total_demand  # Use total_demand (float) not demand_factor (variable)
    )

    # Constraint 2: Price upper bound based on expected market price
    m.addConstr(price <= expected_price_val * 1.5, "upper_bound_market_price")

    # Constraint 3: Minimum price to cover operating costs
    operating_min = (aircraft_cost / (aircraft_capacity * efficiency_factor)) * 1.1  # 10% margin
    m.addConstr(price >= operating_min, "min_operating_cost")

    # Constraint 4: Competitive pricing constraint
    # Price should not exceed 200% of base price for economy, 300% for business/first
    seat_type_lower = ticket.seat_type.lower()
    is_premium_seat = any(premium in seat_type_lower for premium in ["first", "business", "premium"])
    max_price_multiplier = 3.0 if is_premium_seat else 2.0
    m.addConstr(price <= base_price * max_price_multiplier, "competitive_pricing")

    # Constraint 5: Ensure reasonable profit margin (at least 15% above cost)
    m.addConstr(price >= operating_min * 1.15, "minimum_profit_margin")

    # Constraint 6: Price should reflect demand (higher demand = higher price)
    m.addConstr(price >= base_price * (1 + (total_demand - 1) * 0.5), "demand_reflection")

    # -----------------------------
    # OBJECTIVE FUNCTION
    # -----------------------------
    # Maximize profit while considering market competitiveness and load factor
    # Weighted objective:
    # 60% maximize price
    # 20% consider load factor optimization (higher load = higher price)
    # 20% consider demand factor (higher demand = higher price)

    objective = (
            0.6 * price +
            0.2 * (load_factor * 100) +  # Reward higher load factors
            0.2 * (demand_factor * 50)  # Reward higher demand
    )
    m.setObjective(objective, GRB.MAXIMIZE)

    m.optimize()

    if m.status == GRB.OPTIMAL:
        final_price = round(price.X, 2)

        # Print detailed breakdown
        print("\n" + "=" * 50)
        print("TICKET PRICE OPTIMIZATION BREAKDOWN")
        print("=" * 50)
        print(f"Flight: {flight.from_country} → {flight.to_country}")
        print(f"Seat type: {ticket.seat_type}")
        print(f"Base price: ${base_price_value}")
        print(f"Seat factor: {seat_factor}")
        print(f"Adjusted base: ${base_price:.2f}")
        print(f"\nDynamic Factors:")
        print(f"  Load factor: {load_factor * 100:.1f}%")
        print(f"  Is holiday: {'Yes' if is_holiday else 'No'}")
        print(f"  Tourist destination: {'Yes' if is_tourist_destination else 'No'}")
        print(f"  Is weekend: {'Yes' if is_weekend else 'No'}")
        print(f"  Is late booking: {'Yes' if is_late_booking else 'No'}")
        print(f"  Calculated demand factor: {total_demand:.2f}")
        print(f"\nDiscounts/Surcharges:")
        print(f"  Advanced booking: -{adv_discount * 100:.1f}%")
        print(f"  Special offers: -{special_discount_total * 100:.1f}%")
        print(f"  Stop discount: -{stop_discount_val * 100:.1f}%")
        print(f"  Roundtrip: -{roundtrip_discount_val * 100:.1f}%")
        print(f"  Weekend surcharge: +{weekend_surcharge_val * 100:.1f}%")
        print(f"  Holiday surcharge: +{holiday_surcharge * 100:.1f}%")
        print(f"  Late booking: +{late_surcharge * 100:.1f}%")
        print(f"  Luggage surcharge: +{luggage_surcharge_val * 100:.1f}%")
        print(f"  Tourist surcharge: +{tourist_surcharge_val * 100:.1f}%")
        print(f"\nCost Analysis:")
        print(f"  Aircraft cost: ${aircraft_cost:.2f}")
        print(f"  Efficiency factor: {efficiency_factor}")
        print(f"  Aircraft capacity: {aircraft_capacity}")
        print(f"  Aircraft type: {aircraft_type}")
        print(f"  Aircraft cost factor: {aircraft_cost_factor}")
        print(f"  Minimum operating cost: ${operating_min:.2f}")
        print(f"\nOptimized price: ${final_price}")
        print("=" * 50 + "\n")

        return final_price
    else:
        # Fallback: calculate expected price using the float value, not expression
        fallback_price = round(expected_price_val, 2)
        print(f"Optimization failed, using fallback price: ${fallback_price}")
        return fallback_price