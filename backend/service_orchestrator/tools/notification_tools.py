"""
Notification simulation tools.
Simulates SMS, WhatsApp, and push notifications.
"""

from datetime import datetime


def simulate_sms(phone_number: str, message: str) -> dict:
    """Simulate sending an SMS notification to a phone number.

    Args:
        phone_number: The recipient phone number (e.g. '+92-300-1234567').
        message: The SMS message content.

    Returns:
        A dict confirming the simulated SMS delivery.
    """
    return {
        "status": "success",
        "channel": "sms",
        "to": phone_number,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "simulated": True,
        "delivery_status": "delivered",
    }


def simulate_whatsapp(phone_number: str, message: str) -> dict:
    """Simulate sending a WhatsApp message notification.

    Args:
        phone_number: The recipient phone number.
        message: The WhatsApp message content.

    Returns:
        A dict confirming the simulated WhatsApp delivery.
    """
    return {
        "status": "success",
        "channel": "whatsapp",
        "to": phone_number,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "simulated": True,
        "delivery_status": "delivered",
        "read_receipt": False,
    }


def schedule_reminder(
    booking_id: str,
    recipient_phone: str,
    reminder_message: str,
    remind_before_minutes: int = 60,
) -> dict:
    """Schedule a reminder notification before a booking.

    Args:
        booking_id: The booking ID this reminder is for.
        recipient_phone: Phone number to send the reminder to.
        reminder_message: The reminder message text.
        remind_before_minutes: How many minutes before the booking to send the reminder.

    Returns:
        A dict confirming the scheduled reminder.
    """
    return {
        "status": "success",
        "booking_id": booking_id,
        "reminder_scheduled": True,
        "remind_before_minutes": remind_before_minutes,
        "recipient": recipient_phone,
        "message_preview": reminder_message[:100],
        "timestamp": datetime.now().isoformat(),
        "simulated": True,
    }


def simulate_provider_enroute(booking_id: str, provider_name: str, eta_minutes: int = 15) -> dict:
    """Simulate a provider en-route notification to the customer.

    Args:
        booking_id: The booking ID.
        provider_name: The provider's name.
        eta_minutes: Estimated time of arrival in minutes.

    Returns:
        A dict with the en-route notification details.
    """
    return {
        "status": "success",
        "booking_id": booking_id,
        "notification_type": "provider_enroute",
        "message": f"🚗 {provider_name} is on the way! Estimated arrival in {eta_minutes} minutes.",
        "eta_minutes": eta_minutes,
        "timestamp": datetime.now().isoformat(),
        "simulated": True,
    }
