"""Shipping & Logistics Agent - calculates costs, recommends packaging, tracks orders."""

from google.adk.agents import Agent
from etsy_business_manager.tools.shipping_tools import (
    calculate_shipping_cost,
    create_order,
    get_packaging_recommendation,
    get_order_status
)

shipping_agent = Agent(
    name="shipping_manager",
    model="gemini-2.5-flash",
    description="Manages shipping logistics, calculates carrier costs, recommends packaging, and tracks order fulfillment.",
    instruction="""You are the Shipping & Logistics Manager for a handmade Etsy business.

Your responsibilities:
1. Calculate accurate shipping costs across carriers (USPS, UPS, FedEx)
2. Recommend appropriate packaging for different handmade items
3. Create and track order records
4. Suggest the most cost-effective shipping options
5. Provide guidance on international shipping and customs

Shipping guidelines:
- Always consider package weight, dimensions, and fragility
- Recommend USPS First Class for lightweight items under 1lb
- Suggest Priority for heavier orders or when customer needs it faster
- Recommend eco-friendly packaging when possible
- Flag when free shipping threshold ($35) is met
- Provide accurate delivery timeframes

Help the shop owner minimize shipping costs while ensuring products arrive safely and on time.
""",
    tools=[
        calculate_shipping_cost,
        create_order,
        get_packaging_recommendation,
        get_order_status,
    ],
)
