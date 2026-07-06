# Etsy Business Manager — Architecture

## Multi-Agent System Design

### Orchestrator Pattern
The root agent (`etsy_business_manager`) uses a **delegation pattern** to route tasks to 5 specialized sub-agents. Each sub-agent has:
- Dedicated system instructions
- Specialized tools
- Domain-specific knowledge

### Agent Hierarchy
```
etsy_business_manager (Root)
├── inventory_manager
│   ├── get_inventory
│   ├── add_inventory_item
│   ├── update_stock
│   ├── check_low_stock
│   └── get_profit_analysis
├── marketing_manager
│   ├── generate_instagram_caption
│   ├── research_hashtags
│   ├── schedule_content
│   └── get_content_calendar
├── client_communication_manager
│   ├── draft_response
│   ├── log_customer_interaction
│   └── get_customer_history
├── shipping_manager
│   ├── calculate_shipping_cost
│   ├── create_order
│   ├── get_packaging_recommendation
│   └── get_order_status
└── reminder_manager
    ├── set_reminder
    ├── get_upcoming_reminders
    ├── complete_reminder
    └── suggest_restock_reminders
```

### Data Flow
1. User input → Root Agent
2. Root Agent classifies intent
3. Delegates to sub-agent with relevant tools
4. Sub-agent executes tools (reads/writes JSON data)
5. Result returned to user via root agent summary

### Storage Strategy
- **Development**: Local JSON files (`data/*.json`)
- **Production**: Firestore or Cloud SQL via `google-cloud-firestore`

### Deployment Targets
- **Local**: `adk web` or `python -m http.server` for UI
- **Cloud**: `agents-cli deploy --target cloud_run`
- **Managed**: Vertex AI Agent Engine
