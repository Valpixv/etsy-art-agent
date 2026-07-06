"""Reminder & Task tools.

Syntax-error fixed and robust.
"""

import json
import os
from datetime import datetime
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
    priority: str = "medium",
    description: str = ""
) -> str:
    """Set a business reminder.

    Args:
        title: Title of reminder
        due_date: Due date (YYYY-MM-DD)
        reminder_type: restock, craft_fair, tax_deadline, follow_up, supply_run, general
        priority: low, medium, high, urgent
        description: Details or notes

    Returns:
        Confirmation
    """
    os.makedirs(os.path.dirname(REMINDERS_FILE), exist_ok=True)

    if os.path.exists(REMINDERS_FILE):
        with open(REMINDERS_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {"reminders": []}

    rem_id = f"REM-{len(data['reminders']) + 1:04d}"

    reminder = {
        "id": rem_id,
        "title": title,
        "due_date": due_date,
        "reminder_type": reminder_type,
        "priority": priority,
        "description": description,
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }

    data["reminders"].append(reminder)

    with open(REMINDERS_FILE, "w") as f:
        json.dump(data, f, indent=2)

    return f"⏰ Set reminder: '{title}' for {due_date} (ID: {rem_id})"

@tool
def get_upcoming_reminders(days_ahead: int = 7) -> str:
    """Get list of upcoming reminders.

    Args:
        days_ahead: Days range to query

    Returns:
        Reminders list text
    """
    if not os.path.exists(REMINDERS_FILE):
        return "No reminders found. Use set_reminder to create one!"

    with open(REMINDERS_FILE, "r") as f:
        data = json.load(f)

    from datetime import datetime, timedelta
    today = datetime.now().date()
    cutoff = today + timedelta(days=days_ahead)

    active = [r for r in data["reminders"] if r["status"] == "pending"]
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

    result = f"📅 UPCOMING REMINDERS (Next {days_ahead} Days)\n"
    result += "=" * 45 + "\n"

    type_emojis = {
        "restock": "📦", "craft_fair": "🎪", "tax_deadline": "📋",
        "follow_up": "💬", "supply_run": "🛒", "general": "⏰"
    }

    for r, due in upcoming:
        days = (due - today).days
        days_str = "TODAY! 🔥" if days == 0 else f"in {days} days"
        priority_emoji = {"low": "🔵", "medium": "🟡", "high": "🟠", "urgent": "🔴"}.get(r["priority"], "🟡")
        emoji = type_emojis.get(r["reminder_type"], "⏰")

        result += f"\n{priority_emoji} {emoji} {r['title']}\n"
        result += f"   Due: {r['due_date']} ({days_str})\n"
        result += f"   Type: {r['reminder_type']} | Priority: {r['priority']}\n"
        if r['description']:
            result += f"   Note: {r['description']}\n"
        result += f"   ID: {r['id']}\n"

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

    result = "📦 SUGGESTED RESTOCK REMINDERS\n"
    result += "=" * 40 + "\n"

    for item in low_stock:
        result += f"\n🔴 {item['name']} ({item['category']})\n"
        result += f"   Current stock: {item['quantity']} (threshold: {item.get('low_stock_threshold', 5)})\n"
        result += f"   Materials needed: {', '.join(item['materials_used'])}\n"
        result += f"   Suggested action: Restock to ~15-20 units\n"

    result += "\n💡 Tip: Set reminders for supply runs to restock materials!"

    return result
