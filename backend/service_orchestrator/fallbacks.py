import logging
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.registry import LLMRegistry

logger = logging.getLogger(__name__)

async def fallback_to_groq(ctx: CallbackContext, req: LlmRequest, err: Exception):
    """Fallback callback to run a Groq Llama model if Gemini fails."""
    logger.error(f"Primary model {req.model} failed: {err}. Falling back to groq/llama-3.3-70b-versatile.")
    
    # Change the model in the request to the Groq fallback model
    # LiteLLM supports provider/model syntax out of the box.
    req.model = "groq/llama-3.3-70b-versatile"
    
    try:
        # Create a new LLM instance for the fallback model and execute it manually
        fallback_llm = LLMRegistry.new_llm(req.model)
        return await fallback_llm.generate_content(req)
    except Exception as fallback_err:
        logger.error(f"Fallback model also failed: {fallback_err}")
        # Re-raise the original error or the fallback error
        raise fallback_err
