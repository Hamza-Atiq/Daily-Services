import logging
from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.models.lite_llm import LiteLlm

logger = logging.getLogger(__name__)

FALLBACK_MODEL = "groq/llama-3.3-70b-versatile"


async def fallback_to_groq(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
    error: Exception,
) -> Optional[LlmResponse]:
    """on_model_error_callback: route to Groq via LiteLLM when Gemini fails."""
    logger.error(
        "Primary model %s failed: %s. Falling back to %s.",
        llm_request.model, error, FALLBACK_MODEL,
    )

    try:
        # ADK's LiteLlm.generate_content_async uses `llm_request.model or self.model`,
        # so we must overwrite the model on the request — otherwise LiteLLM tries to
        # route the original Gemini model name through Vertex AI and fails.
        llm_request.model = FALLBACK_MODEL
        fallback_llm = LiteLlm(model=FALLBACK_MODEL)
        last_response: Optional[LlmResponse] = None
        async for response in fallback_llm.generate_content_async(llm_request, stream=False):
            last_response = response
        return last_response
    except Exception as fallback_err:
        logger.exception("Fallback model also failed: %s", fallback_err)
        return None
