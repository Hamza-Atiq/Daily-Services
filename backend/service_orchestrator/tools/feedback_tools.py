"""
Feedback and reputation tools.
Handles customer feedback, rating updates, and reputation scoring.
"""

from datetime import datetime


# In-memory feedback store
_feedback_records: list = []


def collect_feedback(
    booking_id: str,
    customer_name: str,
    provider_id: str,
    provider_name: str,
    rating: int,
    review_text: str = "",
    was_on_time: bool = True,
    service_quality: str = "good",
) -> dict:
    """Collect customer feedback after service completion.

    Args:
        booking_id: The booking ID this feedback is for.
        customer_name: Name of the customer giving feedback.
        provider_id: The provider's unique ID.
        provider_name: The provider's name.
        rating: Star rating from 1 to 5.
        review_text: Optional text review from the customer.
        was_on_time: Whether the provider arrived on time.
        service_quality: Quality assessment: 'poor', 'fair', 'good', 'excellent'.

    Returns:
        A dict confirming feedback was recorded and its impact on provider reputation.
    """
    rating = max(1, min(5, rating))

    feedback = {
        "feedback_id": f"FB-{len(_feedback_records)+1:04d}",
        "booking_id": booking_id,
        "customer_name": customer_name,
        "provider_id": provider_id,
        "provider_name": provider_name,
        "rating": rating,
        "review_text": review_text,
        "was_on_time": was_on_time,
        "service_quality": service_quality,
        "timestamp": datetime.now().isoformat(),
    }
    _feedback_records.append(feedback)

    # Calculate reputation impact
    if rating >= 4:
        impact = "positive"
        impact_detail = "Provider ranking will improve for future matching."
    elif rating == 3:
        impact = "neutral"
        impact_detail = "No significant ranking change."
    else:
        impact = "negative"
        impact_detail = "Provider ranking will decrease. If pattern continues, risk score increases."

    if not was_on_time:
        impact_detail += " On-time score reduced due to late arrival."

    # Persist to Firebase
    try:
        from api.core.firebase import get_db
        db = get_db()
        db.collection("feedback").document(feedback["feedback_id"]).set(feedback)
    except Exception:
        pass

    return {
        "status": "success",
        "feedback_id": feedback["feedback_id"],
        "rating_recorded": rating,
        "reputation_impact": impact,
        "impact_detail": impact_detail,
        "message": f"Thank you {customer_name}! Your {rating}-star rating for {provider_name} has been recorded.",
    }


def get_provider_reputation(provider_id: str, provider_name: str) -> dict:
    """Get the reputation summary for a provider based on all feedback.

    Args:
        provider_id: The provider's unique ID.
        provider_name: The provider's name.

    Returns:
        A dict with the provider's reputation summary.
    """
    provider_feedback = [f for f in _feedback_records if f["provider_id"] == provider_id]

    if not provider_feedback:
        return {
            "status": "success",
            "provider_id": provider_id,
            "provider_name": provider_name,
            "total_reviews": 0,
            "message": "No feedback recorded yet.",
        }

    ratings = [f["rating"] for f in provider_feedback]
    on_time_count = sum(1 for f in provider_feedback if f["was_on_time"])

    return {
        "status": "success",
        "provider_id": provider_id,
        "provider_name": provider_name,
        "total_reviews": len(provider_feedback),
        "average_rating": round(sum(ratings) / len(ratings), 2),
        "on_time_percentage": round(on_time_count / len(provider_feedback) * 100, 1),
        "rating_distribution": {str(i): ratings.count(i) for i in range(1, 6)},
        "recent_feedback": provider_feedback[-3:],
    }
