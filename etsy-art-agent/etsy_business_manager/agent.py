"""Etsy Business Manager - Main Orchestrator Agent.

This is the root agent that routes tasks to specialized sub-agents:
- Inventory Manager
- Marketing Manager (Instagram)
- Client Communication Manager
- Shipping & Logistics Manager
- Reminder & Task Manager
"""

from google.adk.agents import Agent
from etsy_business_manager.agents.inventory_agent import inventory_agent
from etsy_business_manager.agents.marketing_agent import marketing_agent
from etsy_business_manager.agents.client_comm_agent import client_communication_agent
from etsy_business_manager.agents.shipping_agent import shipping_agent
from etsy_business_manager.agents.reminder_agent import reminder_agent

# Main orchestrator agent that delegates to sub-agents
root_agent = Agent(
    name="etsy_business_manager",
    model="gemini-2.5-flash",
    description="Multi-agent system for managing a handmade Etsy art business including inventory, marketing, client communication, shipping, and reminders.",
    instruction="""You are the Etsy Business Manager — the central coordinator for a handmade art and craft business.

Your business sells: keychains, jewelry, crochet items, bookmarks, and other handmade crafts.

You manage a team of 5 specialized agents:
1. **inventory_manager** — Use for stock tracking, adding products, checking low stock, profit analysis
2. **marketing_manager** — Use for Instagram captions, hashtags, content calendar, promotions
3. **client_communication_manager** — Use for drafting customer emails, tracking interactions, review responses
4. **shipping_manager** — Use for shipping costs, packaging recommendations, order creation
5. **reminder_manager** — Use for deadlines, restock reminders, craft fair dates, follow-ups

When the user asks something:
- Identify which agent(s) should handle it
- Delegate to the appropriate sub-agent using their tools
- If multiple areas are involved, coordinate between agents
- Always provide clear, actionable summaries

Examples of when to delegate:
- "How many keychains do I have?" → inventory_manager
- "Write an Instagram caption for my new crochet bookmark" → marketing_manager
- "A customer asked about custom jewelry" → client_communication_manager
- "How much to ship 3 items to California?" → shipping_manager
- "Remind me about the craft fair next month" → reminder_manager

Be proactive, organized, and always think about what will help the business run more smoothly.
""",
    sub_agents=[
        inventory_agent,
        marketing_agent,
        client_communication_agent,
        shipping_agent,
        reminder_agent,
    ],
)

if __name__ == "__main__":
    import os
    print("🎨 Etsy Business Manager Orchestrator initialized.")
    print("This file defines the Google ADK root agent configuration.")
    api_key_set = "GEMINI_API_KEY" in os.environ
    print(f"Gemini API Connection: {'🟢 CONFIGURED' if api_key_set else '🔴 MISSING (Offline fallback enabled)'}")
    print("\nTo launch the interactive manager interface, run:")
    print("  python server.py")

