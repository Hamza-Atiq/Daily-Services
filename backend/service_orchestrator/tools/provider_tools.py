"""
Provider tools for finding and ranking service providers.
Reads from Firebase Firestore. Falls back to local JSON seed data.
"""

import json
import math
import os
from datetime import datetime, timedelta
from service_orchestrator.tools.location_tools import _haversine, _LOCATIONS


# ── Local cache (loaded from Firebase or seed file) ──────────────────────────
_providers_cache: list | None = None
_SEED_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "providers_seed.json")


def _load_providers() -> list:
    """Load providers from cache, or seed file as fallback."""
    global _providers_cache
    if _providers_cache is not None:
        return _providers_cache

    try:
        from api.core.firebase import get_db
        db = get_db()
        docs = db.collection("providers").stream()
        _providers_cache = [doc.to_dict() | {"id": doc.id} for doc in docs]
        if _providers_cache:
            return _providers_cache
    except Exception:
        pass

    # Fallback: load from local seed file
    if os.path.exists(_SEED_PATH):
        with open(_SEED_PATH, "r", encoding="utf-8") as f:
            _providers_cache = json.load(f)
    else:
        _providers_cache = []
    return _providers_cache


def find_providers(service_type: str, location_sector: str, max_distance_km: float = 20.0) -> dict:
    """Find service providers matching a service type near a given Islamabad sector.

    Args:
        service_type: The type of service needed (e.g. 'ac_repair', 'plumbing', 'electrical', 'cleaning', 'tutoring', 'mechanic', 'beauty', 'painting', 'carpentry', 'pest_control').
        location_sector: The user's sector in Islamabad (e.g. 'G-13', 'F-10').
        max_distance_km: Maximum distance to search within (default 20 km).

    Returns:
        A dict containing matching providers with their distance from the user.
    """
    providers = _load_providers()
    sector = location_sector.upper().strip()

    if sector not in _LOCATIONS:
        return {"status": "error", "message": f"Unknown sector: {location_sector}"}

    user_loc = _LOCATIONS[sector]
    matching = []

    for p in providers:
        # Check if provider offers this service
        if service_type.lower() not in [s.lower() for s in p.get("services", [])]:
            continue

        # Calculate distance
        p_loc = p.get("location", {})
        dist = _haversine(user_loc["lat"], user_loc["lng"], p_loc.get("lat", 0), p_loc.get("lng", 0))

        if dist <= max_distance_km:
            matching.append({
                "id": p.get("id"),
                "name": p.get("name"),
                "distance_km": dist,
                "rating": p.get("rating", 0),
                "total_reviews": p.get("total_reviews", 0),
                "reliability_score": p.get("reliability_score", 0),
                "on_time_score": p.get("on_time_score", 0),
                "cancellation_rate": p.get("cancellation_rate", 0),
                "hourly_rate": p.get("hourly_rate", 0),
                "visit_fee": p.get("visit_fee", 0),
                "experience_years": p.get("experience_years", 0),
                "specialization": p.get("specialization", ""),
                "certifications": p.get("certifications", []),
                "sector": p_loc.get("sector", ""),
                "languages": p.get("languages", []),
                "phone": p.get("phone", ""),
                "availability": p.get("availability", {}),
                "risk_score": p.get("risk_score", 0),
                "recent_reviews": p.get("recent_reviews", [])[:3],
            })

    matching.sort(key=lambda x: x["distance_km"])

    return {
        "status": "success",
        "service_type": service_type,
        "user_sector": sector,
        "total_found": len(matching),
        "providers": matching,
    }


def rank_providers(
    providers_data: str,
    urgency: str = "normal",
    budget_sensitivity: str = "medium",
    job_complexity: str = "basic",
) -> dict:
    """Rank a list of providers using an 8-factor weighted scoring algorithm.

    Args:
        providers_data: JSON string of providers list from find_providers result (the 'providers' field).
        urgency: How urgent the request is: 'low', 'normal', 'high', or 'emergency'.
        budget_sensitivity: User's budget sensitivity: 'low', 'medium', or 'high'.
        job_complexity: Job complexity level: 'basic', 'intermediate', or 'complex'.

    Returns:
        A dict with ranked providers, scores, and detailed reasoning per provider.
    """
    try:
        providers = json.loads(providers_data) if isinstance(providers_data, str) else providers_data
    except (json.JSONDecodeError, TypeError):
        return {"status": "error", "message": "Invalid providers data format"}

    if not providers:
        return {"status": "no_providers", "message": "No providers to rank", "ranked": []}

    # Adjust weights based on context
    weights = {
        "distance": 0.15,
        "availability": 0.20,
        "rating": 0.15,
        "review_recency": 0.05,
        "reliability": 0.15,
        "specialization": 0.15,
        "price": 0.10,
        "cancellation": 0.05,
    }

    # Shift weights based on urgency
    if urgency == "emergency":
        weights["distance"] = 0.25
        weights["availability"] = 0.25
        weights["price"] = 0.05
    elif urgency == "high":
        weights["distance"] = 0.20
        weights["availability"] = 0.22

    # Shift weights based on budget
    if budget_sensitivity == "high":
        weights["price"] = 0.20
        weights["rating"] = 0.10

    # Normalize weights
    total_w = sum(weights.values())
    weights = {k: v / total_w for k, v in weights.items()}

    # Find min/max for normalization
    max_dist = max(p.get("distance_km", 1) for p in providers) or 1
    max_rate = max(p.get("hourly_rate", 1) for p in providers) or 1

    ranked = []
    for p in providers:
        scores = {}
        reasoning_parts = []

        # 1. Distance (closer = better, inverted)
        dist = p.get("distance_km", max_dist)
        scores["distance"] = max(0, 1 - (dist / max_dist))
        reasoning_parts.append(f"Distance: {dist}km (score: {scores['distance']:.2f})")

        # 2. Availability (simplified: assume available unless noted)
        scores["availability"] = 0.8  # Default: mostly available
        reasoning_parts.append(f"Availability: assumed available (score: {scores['availability']:.2f})")

        # 3. Rating
        scores["rating"] = min(p.get("rating", 0) / 5.0, 1.0)
        reasoning_parts.append(f"Rating: {p.get('rating', 0)}/5 (score: {scores['rating']:.2f})")

        # 4. Review recency (recent reviews weighted higher)
        recent = p.get("recent_reviews", [])
        if recent:
            avg_recent = sum(r.get("rating", 3) for r in recent) / len(recent)
            scores["review_recency"] = min(avg_recent / 5.0, 1.0)
        else:
            scores["review_recency"] = 0.5
        reasoning_parts.append(f"Recent reviews: {len(recent)} (score: {scores['review_recency']:.2f})")

        # 5. Reliability / On-time
        scores["reliability"] = p.get("reliability_score", 0.5)
        reasoning_parts.append(f"Reliability: {p.get('reliability_score', 0)*100:.0f}% (score: {scores['reliability']:.2f})")

        # 6. Specialization match to complexity
        spec_score = 0.5
        certs = p.get("certifications", [])
        exp = p.get("experience_years", 0)
        if job_complexity == "complex" and (certs or exp > 8):
            spec_score = 0.95
        elif job_complexity == "intermediate" and exp > 4:
            spec_score = 0.85
        elif job_complexity == "basic":
            spec_score = 0.75
        scores["specialization"] = spec_score
        reasoning_parts.append(f"Specialization fit for '{job_complexity}' job: (score: {scores['specialization']:.2f})")

        # 7. Price (cheaper = better for budget-sensitive users)
        rate = p.get("hourly_rate", max_rate)
        scores["price"] = max(0, 1 - (rate / max_rate))
        reasoning_parts.append(f"Rate: PKR {rate}/hr (score: {scores['price']:.2f})")

        # 8. Cancellation rate (lower = better)
        cancel = p.get("cancellation_rate", 0.1)
        scores["cancellation"] = max(0, 1 - cancel)
        reasoning_parts.append(f"Cancellation rate: {cancel*100:.0f}% (score: {scores['cancellation']:.2f})")

        # Calculate weighted total
        total_score = sum(scores[k] * weights[k] for k in weights)

        # Risk adjustment
        risk = p.get("risk_score", 0)
        if risk > 0.3:
            total_score *= (1 - risk * 0.3)
            reasoning_parts.append(f"⚠ Risk adjustment applied: risk_score={risk}")

        ranked.append({
            "id": p.get("id"),
            "name": p.get("name"),
            "total_score": round(total_score, 4),
            "factor_scores": {k: round(v, 3) for k, v in scores.items()},
            "weights_used": {k: round(v, 3) for k, v in weights.items()},
            "reasoning": " | ".join(reasoning_parts),
            "distance_km": p.get("distance_km"),
            "rating": p.get("rating"),
            "hourly_rate": p.get("hourly_rate"),
            "visit_fee": p.get("visit_fee"),
            "phone": p.get("phone"),
            "reliability_score": p.get("reliability_score"),
            "cancellation_rate": p.get("cancellation_rate"),
            "experience_years": p.get("experience_years"),
            "certifications": p.get("certifications"),
        })

    ranked.sort(key=lambda x: x["total_score"], reverse=True)

    return {
        "status": "success",
        "total_ranked": len(ranked),
        "ranking_context": {
            "urgency": urgency,
            "budget_sensitivity": budget_sensitivity,
            "job_complexity": job_complexity,
        },
        "ranked_providers": ranked,
    }
