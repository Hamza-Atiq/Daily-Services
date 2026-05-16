"""
Output guardrail callback for ADK agents.
Ensures agent responses are safe, professional, and on-topic.
"""

from google.genai import types


async def output_safety_guardrail(callback_context, **kwargs):
    """Validate agent output before sending to user.
    
    Returns None to allow the response through, or a modified Content.
    """
    # Currently a pass-through — can be extended to filter PII, profanity, etc.
    return None
