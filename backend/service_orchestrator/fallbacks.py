import logging
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.registry import LLMRegistry

logger = logging.getLogger(__name__)

async def fallback_to_groq(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
    error: Exception,
):
    """Fallback callback to run a Groq Llama model if Gemini fails."""
    logger.error(
        f"Primary model {llm_request.model} failed: {error}. "
        "Falling back to groq/llama-3.3-70b-versatile."
    )

    llm_request.model = "groq/llama-3.3-70b-versatile"

    try:
        fallback_llm = LLMRegistry.new_llm(llm_request.model)
        return await fallback_llm.generate_content(llm_request)
    except Exception as fallback_err:
        logger.error(f"Fallback model also failed: {fallback_err}")
        raise fallback_err
