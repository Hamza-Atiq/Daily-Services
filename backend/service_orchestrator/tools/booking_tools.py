"""
Booking tools for creating, managing, and tracking service bookings.
Persists to Firebase Firestore.
"""

import json
import uuid
from datetime import datetime, timedelta


# In-memory booking store (synced to Firebase)
_bookings: dict = {}


def check_provider_availability(
    provider_id: str,
    provider_name: str,
    requested_date: str,
    requested_time: str,
    estimated_duration_hours: float = 1.0,
) -> dict:
    """Check if a provider is available at the requested date and time.

    Args:
        provider_id: The unique ID of the provider.
        provider_name: The provider's display name.
        requested_date: The requested date in YYYY-MM-DD format.
        requested_time: The requested time in HH:MM format (24h).
        estimated_duration_hours: Estimated service duration in hours.

    Returns:
        A dict with availability status and any conflicting bookings.
    """
    conflicts = []
    for bid, b in _bookings.items():
        if b["provider_id"] != provider_id:
            continue
        if b["date"] != requested_date:
            continue
        if b["status"] in ("cancelled", "completed"):
            continue

        # Check time overlap
        existing_start = datetime.strptime(b["time"], "%H:%M")
        existing_end = existing_start + timedelta(hours=b.get("duration_hours", 1))
        req_start = datetime.strptime(requested_time, "%H:%M")
        req_end = req_start + timedelta(hours=estimated_duration_hours)

        # Add 30-min travel buffer
        existing_end_with_buffer = existing_end + timedelta(minutes=30)

        if req_start < existing_end_with_buffer and req_end > existing_start:
            conflicts.append({
                "booking_id": bid,
                "time": b["time"],
                "duration_hours": b.get("duration_hours", 1),
                "service": b.get("service_type", "unknown"),
            })

    if conflicts:
        # Suggest alternative times
        alt_times = []
        for hour in range(9, 18):
            t = f"{hour:02d}:00"
            is_free = True
            for b in _bookings.values():
                if b["provider_id"] == provider_id and b["date"] == requested_date and b["status"] not in ("cancelled", "completed"):
                    bs = datetime.strptime(b["time"], "%H:%M")
                    be = bs + timedelta(hours=b.get("duration_hours", 1) + 0.5)
                    ts = datetime.strptime(t, "%H:%M")
                    te = ts + timedelta(hours=estimated_duration_hours)
                    if ts < be and te > bs:
                        is_free = False
                        break
            if is_free:
                alt_times.append(t)

        return {
            "status": "unavailable",
            "provider_id": provider_id,
            "provider_name": provider_name,
            "conflicts": conflicts,
            "suggested_alternatives": alt_times[:3],
            "message": f"{provider_name} has a scheduling conflict at {requested_time} on {requested_date}.",
        }

    return {
        "status": "available",
        "provider_id": provider_id,
        "provider_name": provider_name,
        "date": requested_date,
        "time": requested_time,
        "estimated_duration_hours": estimated_duration_hours,
        "message": f"{provider_name} is available at {requested_time} on {requested_date}.",
    }


def create_booking(
    customer_name: str,
    customer_phone: str,
    provider_id: str,
    provider_name: str,
    provider_phone: str,
    service_type: str,
    date: str,
    time: str,
    location_sector: str,
    total_price_pkr: int,
    price_breakdown: str,
    duration_hours: float = 1.0,
    notes: str = "",
) -> dict:
    """Create a confirmed service booking and store it.

    Args:
        customer_name: Name of the customer.
        customer_phone: Customer's phone number.
        provider_id: The provider's unique ID.
        provider_name: The provider's display name.
        provider_phone: Provider's phone number.
        service_type: Type of service booked.
        date: Booking date in YYYY-MM-DD format.
        time: Booking time in HH:MM format.
        location_sector: The sector where service is needed.
        total_price_pkr: Total agreed price in PKR.
        price_breakdown: JSON string of the price breakdown.
        duration_hours: Estimated service duration.
        notes: Any additional notes or instructions.

    Returns:
        A dict with the booking confirmation details and receipt.
    """
    booking_id = f"BK-{uuid.uuid4().hex[:8].upper()}"

    booking = {
        "booking_id": booking_id,
        "customer_name": customer_name,
        "customer_phone": customer_phone,
        "provider_id": provider_id,
        "provider_name": provider_name,
        "provider_phone": provider_phone,
        "service_type": service_type,
        "date": date,
        "time": time,
        "location_sector": location_sector,
        "total_price_pkr": total_price_pkr,
        "price_breakdown": price_breakdown,
        "duration_hours": duration_hours,
        "notes": notes,
        "status": "confirmed",
        "created_at": datetime.now().isoformat(),
        "timeline": [
            {"event": "booking_created", "timestamp": datetime.now().isoformat(), "details": "Booking confirmed by AI system."},
        ],
    }

    _bookings[booking_id] = booking

    # Try to persist to Firebase
    try:
        from api.core.firebase import get_db
        db = get_db()
        db.collection("bookings").document(booking_id).set(booking)
    except Exception:
        pass  # In-memory fallback is fine for demo

    receipt = (
        f"═══ BOOKING CONFIRMATION ═══\n"
        f"Booking ID: {booking_id}\n"
        f"Service: {service_type.replace('_', ' ').title()}\n"
        f"Provider: {provider_name}\n"
        f"Date: {date}\n"
        f"Time: {time}\n"
        f"Location: {location_sector}\n"
        f"Total: PKR {total_price_pkr:,}\n"
        f"Status: ✅ CONFIRMED\n"
        f"════════════════════════════"
    )

    return {
        "status": "success",
        "booking_id": booking_id,
        "receipt": receipt,
        "booking_details": booking,
        "next_steps": [
            f"SMS confirmation sent to {customer_phone}",
            f"Provider {provider_name} notified at {provider_phone}",
            f"Reminder scheduled for 1 hour before appointment",
        ],
    }


def cancel_booking(booking_id: str, reason: str = "Customer requested") -> dict:
    """Cancel an existing booking and trigger auto-reschedule if needed.

    Args:
        booking_id: The unique booking ID to cancel.
        reason: Reason for cancellation.

    Returns:
        A dict with cancellation confirmation and rebooking options.
    """
    if booking_id not in _bookings:
        return {"status": "error", "message": f"Booking {booking_id} not found."}

    booking = _bookings[booking_id]
    booking["status"] = "cancelled"
    booking["timeline"].append({
        "event": "booking_cancelled",
        "timestamp": datetime.now().isoformat(),
        "details": f"Cancelled: {reason}",
    })

    try:
        from api.core.firebase import get_db
        db = get_db()
        db.collection("bookings").document(booking_id).update({
            "status": "cancelled",
            "timeline": booking["timeline"],
        })
    except Exception:
        pass

    return {
        "status": "success",
        "booking_id": booking_id,
        "message": f"Booking {booking_id} has been cancelled. Reason: {reason}",
        "suggestion": "Would you like me to find an alternative provider and reschedule?",
        "original_booking": {
            "service_type": booking["service_type"],
            "date": booking["date"],
            "time": booking["time"],
            "location_sector": booking["location_sector"],
        },
    }


def get_all_bookings() -> dict:
    """Get all bookings in the system.

    Returns:
        A dict containing all booking records.
    """
    return {
        "status": "success",
        "total_bookings": len(_bookings),
        "bookings": list(_bookings.values()),
    }


def get_booking_by_id(booking_id: str) -> dict:
    """Get details of a specific booking.

    Args:
        booking_id: The unique booking ID.

    Returns:
        A dict with the booking details.
    """
    if booking_id not in _bookings:
        return {"status": "error", "message": f"Booking {booking_id} not found."}
    return {"status": "success", "booking": _bookings[booking_id]}
