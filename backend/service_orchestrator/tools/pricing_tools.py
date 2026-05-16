"""
Dynamic pricing tools for the Service Orchestrator.
Calculates transparent price quotes with detailed breakdowns.
"""

import json
from datetime import datetime


# ── Base rates for service types (PKR) ───────────────────────────────────────
BASE_RATES = {
    "ac_repair": {"visit_fee": 400, "hourly_rate": 800, "basic": 1500, "intermediate": 3500, "complex": 8000},
    "ac_installation": {"visit_fee": 500, "hourly_rate": 1000, "basic": 3000, "intermediate": 6000, "complex": 12000},
    "ac_maintenance": {"visit_fee": 300, "hourly_rate": 600, "basic": 1200, "intermediate": 2500, "complex": 5000},
    "plumbing": {"visit_fee": 300, "hourly_rate": 600, "basic": 1000, "intermediate": 3000, "complex": 7000},
    "electrical": {"visit_fee": 350, "hourly_rate": 700, "basic": 1200, "intermediate": 3500, "complex": 8000},
    "cleaning": {"visit_fee": 0, "hourly_rate": 500, "basic": 1500, "intermediate": 3000, "complex": 6000},
    "tutoring": {"visit_fee": 0, "hourly_rate": 800, "basic": 800, "intermediate": 1500, "complex": 3000},
    "mechanic": {"visit_fee": 500, "hourly_rate": 700, "basic": 1500, "intermediate": 4000, "complex": 10000},
    "beauty": {"visit_fee": 0, "hourly_rate": 600, "basic": 1000, "intermediate": 2500, "complex": 5000},
    "painting": {"visit_fee": 0, "hourly_rate": 500, "basic": 2000, "intermediate": 5000, "complex": 12000},
    "carpentry": {"visit_fee": 400, "hourly_rate": 700, "basic": 2000, "intermediate": 5000, "complex": 10000},
    "pest_control": {"visit_fee": 300, "hourly_rate": 600, "basic": 2000, "intermediate": 4000, "complex": 8000},
}

# Surge multipliers
URGENCY_MULTIPLIERS = {
    "low": 0.95,       # Discount for flexible timing
    "normal": 1.0,
    "high": 1.15,      # 15% surcharge
    "emergency": 1.35,  # 35% surcharge
}

# Peak hours demand factor
PEAK_HOURS = {
    "morning": 1.05,    # 8-12 AM slight demand
    "afternoon": 1.0,
    "evening": 1.10,    # 5-9 PM higher demand
    "night": 1.25,      # After hours premium
}

# Seasonal factors (Pakistan climate)
SEASONAL_FACTORS = {
    "ac_repair": {"5": 1.20, "6": 1.30, "7": 1.35, "8": 1.30, "9": 1.15},  # Summer surge
    "ac_installation": {"4": 1.15, "5": 1.25, "6": 1.30, "7": 1.20},
}


def calculate_price(
    service_type: str,
    job_complexity: str,
    provider_hourly_rate: int,
    provider_visit_fee: int,
    distance_km: float,
    urgency: str = "normal",
    time_of_day: str = "morning",
    is_returning_customer: bool = False,
) -> dict:
    """Calculate a dynamic price quote with a transparent breakdown.

    Args:
        service_type: Type of service (e.g. 'ac_repair', 'plumbing').
        job_complexity: Complexity level: 'basic', 'intermediate', or 'complex'.
        provider_hourly_rate: The provider's hourly rate in PKR.
        provider_visit_fee: The provider's visit fee in PKR.
        distance_km: Distance from provider to user in km.
        urgency: Urgency level: 'low', 'normal', 'high', or 'emergency'.
        time_of_day: Time of day: 'morning', 'afternoon', 'evening', or 'night'.
        is_returning_customer: Whether the user is a returning customer for loyalty discount.

    Returns:
        A dict with detailed price breakdown, total, and fairness analysis.
    """
    base = BASE_RATES.get(service_type.lower(), BASE_RATES["plumbing"])
    complexity_base = base.get(job_complexity, base["basic"])

    breakdown = {}

    # 1. Base service cost
    breakdown["base_service_cost"] = complexity_base
    explanation = [f"Base cost for {job_complexity} {service_type}: PKR {complexity_base}"]

    # 2. Visit fee
    visit_fee = max(provider_visit_fee, base["visit_fee"])
    breakdown["visit_fee"] = visit_fee
    if visit_fee > 0:
        explanation.append(f"Visit fee: PKR {visit_fee}")

    # 3. Distance surcharge (PKR 15/km beyond 5km)
    distance_charge = 0
    if distance_km > 5:
        distance_charge = int((distance_km - 5) * 15)
        breakdown["distance_surcharge"] = distance_charge
        explanation.append(f"Distance surcharge ({distance_km:.1f}km, beyond 5km free): PKR {distance_charge}")
    else:
        breakdown["distance_surcharge"] = 0

    # 4. Urgency multiplier
    urgency_mult = URGENCY_MULTIPLIERS.get(urgency, 1.0)
    urgency_adjustment = int(complexity_base * (urgency_mult - 1))
    breakdown["urgency_adjustment"] = urgency_adjustment
    if urgency_adjustment != 0:
        explanation.append(f"Urgency ({urgency}): {'+' if urgency_adjustment > 0 else ''}{urgency_adjustment} PKR ({urgency_mult:.0%})")

    # 5. Demand / time-of-day
    demand_mult = PEAK_HOURS.get(time_of_day, 1.0)
    demand_adjustment = int(complexity_base * (demand_mult - 1))
    breakdown["demand_adjustment"] = demand_adjustment
    if demand_adjustment > 0:
        explanation.append(f"Peak hours ({time_of_day}): +{demand_adjustment} PKR")

    # 6. Seasonal factor
    month = str(datetime.now().month)
    seasonal = SEASONAL_FACTORS.get(service_type, {}).get(month, 1.0)
    seasonal_adjustment = int(complexity_base * (seasonal - 1))
    breakdown["seasonal_adjustment"] = seasonal_adjustment
    if seasonal_adjustment > 0:
        explanation.append(f"Seasonal demand (month {month}): +{seasonal_adjustment} PKR")

    # 7. Loyalty discount
    loyalty_discount = 0
    if is_returning_customer:
        loyalty_discount = int(complexity_base * 0.10)
        breakdown["loyalty_discount"] = -loyalty_discount
        explanation.append(f"Returning customer discount: -{loyalty_discount} PKR (10%)")
    else:
        breakdown["loyalty_discount"] = 0

    # Calculate total
    total = (
        complexity_base
        + visit_fee
        + distance_charge
        + urgency_adjustment
        + demand_adjustment
        + seasonal_adjustment
        - loyalty_discount
    )

    # Budget alternative (strip urgency + demand, use base rates)
    budget_total = complexity_base + base["visit_fee"]
    budget_note = f"Budget option (flexible timing, standard provider): PKR {budget_total}"

    # Fairness analysis
    provider_earning = total - visit_fee  # Rough estimate
    market_avg = base.get(job_complexity, base["basic"])
    fairness = "fair"
    if total > market_avg * 1.5:
        fairness = "above_market"
    elif total < market_avg * 0.75:
        fairness = "below_market"

    return {
        "status": "success",
        "total_price_pkr": total,
        "currency": "PKR",
        "breakdown": breakdown,
        "explanation": explanation,
        "budget_alternative": {"total_pkr": budget_total, "note": budget_note},
        "fairness_analysis": {
            "verdict": fairness,
            "market_average_pkr": market_avg,
            "provider_estimated_earning_pkr": provider_earning,
            "user_total_pkr": total,
        },
        "context": {
            "service_type": service_type,
            "job_complexity": job_complexity,
            "urgency": urgency,
            "distance_km": distance_km,
        },
    }
