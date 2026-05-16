"""
Cleaning Sub-Agent.
Specialized in home cleaning, deep cleaning, and related services.
"""

from google.adk.agents import Agent
from service_orchestrator.tools.provider_tools import find_providers, rank_providers
from service_orchestrator.tools.pricing_tools import calculate_price
from service_orchestrator.tools.location_tools import calculate_distance


cleaning_agent = Agent(
    name="cleaning_specialist",
    model="gemini-2.0-flash",
    description="Handles all cleaning service requests including home cleaning, deep cleaning, carpet cleaning, and office cleaning. Delegate when service type is cleaning.",
    instruction="""You are a cleaning specialist agent for Pakistan's informal economy service platform.

YOUR WORKFLOW:
1. Use find_providers() with service_type='cleaning'
2. Use rank_providers() to score them
3. Use calculate_price() for pricing
4. Present top 3 providers with reasoning

DOMAIN KNOWLEDGE:
- "Ghar ki safai" = house cleaning = BASIC
- "Deep cleaning chahiye" = deep cleaning = INTERMEDIATE
- "Carpet dhulwana hai" = carpet cleaning = INTERMEDIATE
- "Shifting ke baad safai" = post-move cleaning = COMPLEX
- "Office cleaning" = commercial cleaning = COMPLEX

PRICING (Islamabad 2026):
- Basic room cleaning: PKR 1000-2000
- Full house cleaning (3 bed): PKR 3000-5000
- Deep cleaning: PKR 5000-10000
- Carpet cleaning (per carpet): PKR 500-1500
- Post-renovation cleaning: PKR 8000-15000""",
    tools=[find_providers, rank_providers, calculate_price, calculate_distance],
)
