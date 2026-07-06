"""Inventory management tools for the Etsy Business Manager."""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

try:
    from google.adk.tools import tool
except ImportError:
    # Fallback decorator for when ADK is not installed
    def tool(func):
        return func

INVENTORY_FILE = "etsy_business_manager/data/inventory.json"

class InventoryItem(BaseModel):
    item_id: str
    name: str
    category: str  # keychains, jewelry, crochet, bookmarks, etc.
    description: str
    quantity: int
    material_cost: float
    selling_price: float
    materials_used: List[str]
    time_to_make_minutes: int
    tags: List[str]
    last_restocked: str
    low_stock_threshold: int = 5

class InventoryUpdate(BaseModel):
    item_id: str
    quantity_change: int  # positive for restock, negative for sale
    notes: str = ""

@tool
def get_inventory(category: Optional[str] = None) -> str:
    """Get current inventory. Optionally filter by category.

    Args:
        category: Filter by category (e.g., 'jewelry', 'crochet', 'keychains', 'bookmarks')

    Returns:
        JSON string of inventory items
    """
    if not os.path.exists(INVENTORY_FILE):
        return json.dumps({"items": [], "message": "No inventory found."})

    with open(INVENTORY_FILE, "r") as f:
        data = json.load(f)

    items = data.get("items", [])
    if category:
        items = [item for item in items if item["category"].lower() == category.lower()]

    return json.dumps({"items": items, "count": len(items)}, indent=2)

@tool
def add_inventory_item(
    name: str,
    category: str,
    description: str,
    quantity: int,
    material_cost: float,
    selling_price: float,
    materials_used: List[str],
    time_to_make_minutes: int,
    tags: List[str]
) -> str:
    """Add a new handmade item to inventory.

    Args:
        name: Product name
        category: Category (keychains, jewelry, crochet, bookmarks, etc.)
        description: Product description
        quantity: Current stock quantity
        material_cost: Cost of materials to make one item
        selling_price: Selling price on Etsy
        materials_used: List of materials used
        time_to_make_minutes: Time to create one item
        tags: Search tags for the item

    Returns:
        Confirmation message with item ID
    """
    os.makedirs(os.path.dirname(INVENTORY_FILE), exist_ok=True)

    if os.path.exists(INVENTORY_FILE):
        with open(INVENTORY_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {"items": []}

    item_id = f"{category[:3].upper()}-{len(data['items']) + 1:04d}"

    item = {
        "item_id": item_id,
        "name": name,
        "category": category,
        "description": description,
        "quantity": quantity,
        "material_cost": material_cost,
        "selling_price": selling_price,
        "materials_used": materials_used,
        "time_to_make_minutes": time_to_make_minutes,
        "tags": tags,
        "last_restocked": datetime.now().isoformat(),
        "low_stock_threshold": 5
    }

    data["items"].append(item)

    with open(INVENTORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

    return f"✅ Added '{name}' (ID: {item_id}) to inventory. Stock: {quantity}"

@tool
def update_stock(item_id: str, quantity_change: int, notes: str = "") -> str:
    """Update stock quantity for an item.

    Args:
        item_id: The item ID to update
        quantity_change: Amount to add (positive) or remove (negative)
        notes: Reason for the update

    Returns:
        Updated stock information
    """
    if not os.path.exists(INVENTORY_FILE):
        return "❌ No inventory file found."

    with open(INVENTORY_FILE, "r") as f:
        data = json.load(f)

    for item in data["items"]:
        if item["item_id"] == item_id:
            item["quantity"] += quantity_change
            if item["quantity"] < 0:
                item["quantity"] = 0
            item["last_restocked"] = datetime.now().isoformat()

            with open(INVENTORY_FILE, "w") as f:
                json.dump(data, f, indent=2)

            alert = ""
            if item["quantity"] <= item["low_stock_threshold"]:
                alert = f" ⚠️ LOW STOCK ALERT: Only {item['quantity']} left!"

            return f"📦 Updated {item['name']}: {item['quantity']} in stock.{alert}"

    return f"❌ Item {item_id} not found."

@tool
def check_low_stock() -> str:
    """Check for items running low on stock.

    Returns:
        List of low-stock items
    """
    if not os.path.exists(INVENTORY_FILE):
        return "No inventory file found."

    with open(INVENTORY_FILE, "r") as f:
        data = json.load(f)

    low_stock = [
        item for item in data["items"]
        if item["quantity"] <= item["low_stock_threshold"]
    ]

    if not low_stock:
        return "✅ All items are well-stocked!"

    result = "⚠️ LOW STOCK ITEMS:\n"
    for item in low_stock:
        result += f"  • {item['name']} ({item['category']}): {item['quantity']} left (ID: {item['item_id']})\n"

    return result

@tool
def get_profit_analysis(item_id: Optional[str] = None) -> str:
    """Calculate profit margins for items.

    Args:
        item_id: Optional specific item ID. If None, analyzes all items.

    Returns:
        Profit analysis report
    """
    if not os.path.exists(INVENTORY_FILE):
        return "No inventory file found."

    with open(INVENTORY_FILE, "r") as f:
        data = json.load(f)

    items = data["items"]
    if item_id:
        items = [item for item in items if item["item_id"] == item_id]

    result = "📊 PROFIT ANALYSIS\n" + "=" * 40 + "\n"
    total_value = 0
    total_cost = 0

    for item in items:
        profit = item["selling_price"] - item["material_cost"]
        margin = (profit / item["selling_price"] * 100) if item["selling_price"] > 0 else 0
        hourly_rate = (profit / item["time_to_make_minutes"] * 60) if item["time_to_make_minutes"] > 0 else 0

        result += f"\n{item['name']} ({item['item_id']}):\n"
        result += f"  Selling: ${item['selling_price']:.2f}\n"
        result += f"  Material Cost: ${item['material_cost']:.2f}\n"
        result += f"  Profit: ${profit:.2f} ({margin:.1f}%)\n"
        result += f"  Hourly Rate: ${hourly_rate:.2f}/hr\n"

        total_value += item["selling_price"] * item["quantity"]
        total_cost += item["material_cost"] * item["quantity"]

    result += f"\n💰 Total Inventory Value: ${total_value:.2f}"
    result += f"\n📦 Total Material Cost: ${total_cost:.2f}"
    result += f"\n📈 Potential Profit: ${total_value - total_cost:.2f}"

    return result
