"""
Input guardrail callback for ADK agents.
Blocks irrelevant, harmful, or out-of-scope requests.
"""

from google.genai import types


BLOCKED_TOPICS = [
    "hack", "illegal", "weapon", "drug", "bomb", "terrorism",
    "credit card number", "password", "social security",
]

SERVICE_KEYWORDS = [
    "ac", "air conditioner", "plumber", "plumbing", "electric", "bijli", "wiring",
    "tutor", "teacher", "padhai", "cleaning", "safai", "mechanic", "car", "gaari",
    "beauty", "parlour", "salon", "paint", "rang", "carpenter", "lakri",
    "pest", "keera", "cockroach", "book", "cancel", "dispute", "complain",
    "feedback", "rating", "price", "service", "repair", "fix", "install",
    "technician", "provider", "help", "chahiye", "zaroorat", "kaam",
    "booking", "schedule", "available", "cost", "kitna", "kharcha",
]


async def input_safety_guardrail(callback_context, **kwargs):
    """Block harmful or irrelevant requests before they reach the agent.
    
    Returns None to allow processing, or a Content to short-circuit.
    """
    # Get the latest user message from invocation context
    user_message = ""
    if hasattr(callback_context, 'user_content'):
        parts = callback_context.user_content.parts if callback_context.user_content else []
        user_message = " ".join(p.text for p in parts if hasattr(p, 'text'))
    
    if not user_message:
        return None  # Allow through if no message

    msg_lower = user_message.lower()

    # Block harmful content
    for blocked in BLOCKED_TOPICS:
        if blocked in msg_lower:
            return types.Content(
                parts=[types.Part.from_text(
                    text="I'm sorry, I can only help with home service requests like plumbing, AC repair, "
                         "electrical work, cleaning, tutoring, and other professional services. "
                         "Please ask me about a service you need! 🏠"
                )]
            )

    return None  # Allow all other messages through
