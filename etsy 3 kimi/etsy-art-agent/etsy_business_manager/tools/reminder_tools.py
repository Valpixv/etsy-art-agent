"""Reminder, deadline, and task management tools."""

import json
import os
from datetime import datetime, timedelta
from typing import Optional

try:
    from google.adk.tools import tool
except ImportError:
    def tool(func):
        return func

REMINDERS_FILE = "etsy_business_manager/data/reminders.json"

@tool
def set_reminder(
    title: str,
    due_date: str,
    reminder_type: str = "general",
    description: str = "",
    priority: str = "medium",
    repeat: str = "none"
) -> str:
    """Set a reminder or deadline.

    Args:
        title: Reminder title
        due_date: Due date (YYYY-MM-DD) or datetime (YYYY-MM-DD HH:MM)
        reminder_type: Type (restock, craft_fair, tax_deadline, follow_up, supply_run, general)
        description: Additional details
        priority: Priority level (low, medium, high, urgent)
        repeat: Repeat frequency (none, daily, weekly, monthly, yearly)

    Returns:
        Confirmation of set reminder
    """
    os.makedirs(os.path.dirname(REMINDERS_FILE), exist_ok=True)

    if os.path.exists(REMINDERS_FILE):
        with open(REMINDERS_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {"reminders": []}

    reminder = {
        "id": f"REM-{len(data['reminders']) + 1:04d}",
        "title": title,
        "due_date": due_date,
        "reminder_type": reminder_type,
        "description": description,
        "priority": priority,
        "repeat": repeat,
        "status": "active",
        "created_at": datetime.now().isoformat()
    }

    data["reminders"].append(reminder)

    with open(REMINDERS_FILE, "w") as f:
        json.dump(data, f, indent=2)

    # Calculate days until due
    try:
        due = datetime.strptime(due_date, "%Y-%m-%d")
        days_until = (due - datetime.now()).days
        time_str = f"({days_until} days away)" if days_until > 0 else "(TODAY!)" if days_until == 0 else "(OVERDUE)"
    except:
        time_str = ""

    type_emojis = {
        "restock": "📦",
        "craft_fair": "🎪",
        "tax_deadline": "📋",
        "follow_up": "💬",
        "supply_run": "🛒",
        "general": "⏰"
    }

    emoji = type_emojis.get(reminder_type, "⏰")
    priority_emoji = {"low": "🔵", "medium": "🟡", "high": "🟠", "urgent": "🔴"}.get(priority, "🟡")

    return f"{emoji} {priority_emoji} Reminder set: '{title}' for {due_date} {time_str} (ID: {reminder['id']})"

@tool
def get_upcoming_reminders(days_ahead: int = 7) -> str:
    """Get upcoming reminders and deadlines.

    Args:
        days_ahead: Number of days to look ahead

    Returns:
        List of upcoming reminders
    """
    if not os.path.exists(REMINDERS_FILE):
        return "📅 No reminders set. Use set_reminder to create some!"

    with open(REMINDERS_FILE, "r") as f:
        data = json.load(f)

    today = datetime.now().date()
    cutoff = today + timedelta(days=days_ahead)

    active = [
        r for r in data["reminders"]
        if r["status"] == "active"
    ]

    upcoming = []
    for r in active:
        try:
            due = datetime.strptime(r["due_date"], "%Y-%m-%d").date()
            if due <= cutoff:
                upcoming.append((r, due))
        except:
            pass

    upcoming.sort(key=lambda x: x[1])

    if not upcoming:
        return f"📅 No upcoming reminders for the next {days_ahead} days. You're all caught up! ✨"

    result = f"📅 UPCOMING REMINDERS (Next {days_ahead} Days)
"
    result += "=" * 45 + "
"

    type_emojis = {
        "restock": "📦", "craft_fair": "🎪", "tax_deadline": "📋",
        "follow_up": "💬", "supply_run": "🛒", "general": "⏰"
    }

    for r, due in upcoming:
        days = (due - today).days
        days_str = "TODAY! 🔥" if days == 0 else f"in {days} days"
        priority_emoji = {"low": "🔵", "medium": "🟡", "high": "🟠", "urgent": "🔴"}.get(r["priority"], "🟡")
        emoji = type_emojis.get(r["reminder_type"], "⏰")

        result += f"
{priority_emoji} {emoji} {r['title']}
"
        result += f"   Due: {r['due_date']} ({days_str})
"
        result += f"   Type: {r['reminder_type']} | Priority: {r['priority']}
"
        if r['description']:
            result += f"   Note: {r['description']}
"
        result += f"   ID: {r['id']}
"

    return result

@tool
def complete_reminder(reminder_id: str) -> str:
    """Mark a reminder as completed.

    Args:
        reminder_id: ID of the reminder to complete

    Returns:
        Confirmation
    """
    if not os.path.exists(REMINDERS_FILE):
        return "No reminders found."

    with open(REMINDERS_FILE, "r") as f:
        data = json.load(f)

    for r in data["reminders"]:
        if r["id"] == reminder_id:
            r["status"] = "completed"
            r["completed_at"] = datetime.now().isoformat()

            with open(REMINDERS_FILE, "w") as f:
                json.dump(data, f, indent=2)

            return f"✅ Completed: '{r['title']}' (ID: {reminder_id})"

    return f"Reminder {reminder_id} not found."

@tool
def suggest_restock_reminders() -> str:
    """Analyze inventory and suggest restock reminders.

    Returns:
        Suggested restock reminders based on low stock
    """
    inventory_file = "etsy_business_manager/data/inventory.json"

    if not os.path.exists(inventory_file):
        return "No inventory data found."

    with open(inventory_file, "r") as f:
        data = json.load(f)

    low_stock = [
        item for item in data.get("items", [])
        if item["quantity"] <= item.get("low_stock_threshold", 5)
    ]

    if not low_stock:
        return "✅ All items are well-stocked! No restock reminders needed."

    result = "📦 SUGGESTED RESTOCK REMINDERS
"
    result += "=" * 40 + "
"

    for item in low_stock:
        result += f"
🔴 {item['name']} ({item['category']})
"
        result += f"   Current stock: {item['quantity']} (threshold: {item.get('low_stock_threshold', 5)})
"
        result += f"   Materials needed: {', '.join(item['materials_used'])}
"
        result += f"   Suggested action: Restock to ~15-20 units
"

    result += "
💡 Tip: Set reminders for supply runs to restock materials!"

    return result
