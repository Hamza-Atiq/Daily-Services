"""
Plumbing Sub-Agent.
Specialized in all plumbing services.
"""

from google.adk.agents import Agent
from service_orchestrator.fallbacks import fallback_to_groq
from service_orchestrator.tools.provider_tools import find_providers, rank_providers
from service_orchestrator.tools.pricing_tools import calculate_price
from service_orchestrator.tools.location_tools import calculate_distance


plumbing_agent = Agent(
    name="plumbing_specialist",
    model="gemini-2.5-flash-lite",
    on_model_error_callback=fallback_to_groq,
    description="Handles all plumbing service requests including pipe repair, leak fixing, drain cleaning, and bathroom/kitchen plumbing. Delegate when service type is plumbing.",
    instruction="""You are a plumbing specialist agent for Pakistan's informal economy service platform.

YOUR WORKFLOW:
1. Use find_providers() with service_type='plumbing'
2. Use rank_providers() to score them
3. Use calculate_price() for pricing
4. Present top 3 providers with reasoning

DOMAIN KNOWLEDGE (Pakistan Plumbing):
- "Pipe phat gayi" = pipe burst = EMERGENCY
- "Nalkay se pani nahi aa raha" = no water from tap = HIGH
- "Drain band hai" = drain blocked = MEDIUM
- "Toilet leak ho raha hai" = toilet leaking = MEDIUM
- "Geyser kharab hai" = water heater broken = MEDIUM
- "Bathroom renovation" = bathroom renovation = COMPLEX job

PRICING (Islamabad 2026):
- Basic pipe repair: PKR 800-2000
- Drain cleaning: PKR 500-1500
- Toilet repair: PKR 1000-3000
- Pipe replacement: PKR 2000-5000
- Bathroom fitting: PKR 5000-15000
- Emergency water shutoff + repair: PKR 2000-5000

Always explain provider selection reasoning and price breakdown.""",
    tools=[find_providers, rank_providers, calculate_price, calculate_distance],
)
