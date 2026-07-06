"""Shipping cost calculation and logistics tools."""

import json
import os
from datetime import datetime
from typing import Optional

try:
    from google.adk.tools import tool
except ImportError:
    def tool(func):
        return func

SHIPPING_RATES_FILE = "etsy_business_manager/data/shipping_rates.json"
ORDERS_FILE = "etsy_business_manager/data/orders.json"

# Simplified shipping rate structure (USD)
SHIPPING_RATES = {
    "USPS": {
        "First Class": {
            "0-4oz": 4.50, "4-8oz": 5.50, "8-12oz": 6.50, "12-16oz": 7.50
        },
        "Priority": {
            "0-1lb": 9.50, "1-2lb": 12.50, "2-3lb": 15.50, "3-5lb": 21.50
        },
        "Flat Rate": {
            "Envelope": 9.65, "Small Box": 10.40, "Medium Box": 17.05, "Large Box": 24.70
        }
    },
    "UPS": {
        "Ground": {
            "0-1lb": 10.50, "1-2lb": 13.50, "2-3lb": 16.50, "3-5lb": 22.50, "5-10lb": 32.50
        },
        "3 Day Select": {
            "0-1lb": 18.50, "1-2lb": 22.50, "2-3lb": 26.50, "3-5lb": 34.50, "5-10lb": 48.50
        }
    },
    "FedEx": {
        "Ground": {
            "0-1lb": 10.00, "1-2lb": 13.00, "2-3lb": 16.00, "3-5lb": 22.00, "5-10lb": 32.00
        },
        "Express": {
            "0-1lb": 28.00, "1-2lb": 32.00, "2-3lb": 36.00, "3-5lb": 44.00, "5-10lb": 58.00
        }
    }
}

@tool
def calculate_shipping_cost(
    weight_oz: float,
    carrier: str = "USPS",
    service_type: str = "First Class",
    destination: str = "domestic",
    package_type: str = "standard"
) -> str:
    """Calculate shipping cost for an order.

    Args:
        weight_oz: Package weight in ounces
        carrier: Shipping carrier (USPS, UPS, FedEx)
        service_type: Service level (First Class, Priority, Ground, Express, etc.)
        destination: domestic or international
        package_type: Type of packaging (standard, envelope, small_box, etc.)

    Returns:
        Shipping cost breakdown
    """

    if destination.lower() == "international":
        # Simplified international markup
        base = weight_oz * 1.5 + 15.0
        return f"🌍 INTERNATIONAL SHIPPING ({carrier})
Weight: {weight_oz}oz
Estimated: ${base:.2f}
Note: Actual cost may vary by country."

    # Domestic calculation
    carrier_rates = SHIPPING_RATES.get(carrier, SHIPPING_RATES["USPS"])
    service_rates = carrier_rates.get(service_type, carrier_rates.get("First Class", carrier_rates.get("Ground")))

    # Find appropriate weight bracket
    weight_lb = weight_oz / 16

    if package_type in ["envelope", "small_box", "medium_box", "large_box"] and "Flat Rate" in carrier_rates:
        cost = carrier_rates["Flat Rate"].get(package_type.capitalize(), 
              carrier_rates["Flat Rate"].get("Envelope", 9.65))
    else:
        # Find weight bracket
        cost = None
        for bracket, rate in service_rates.items():
            if "-" in bracket:
                low, high = bracket.replace("oz", "").replace("lb", "").split("-")
                unit = "oz" if "oz" in bracket else "lb"
                low_val = float(low)
                high_val = float(high)
                current = weight_oz if unit == "oz" else weight_lb
                if low_val <= current <= high_val:
                    cost = rate
                    break

        if cost is None:
            # Default to highest bracket
            cost = list(service_rates.values())[-1]

    # Packaging cost estimate
    packaging_cost = 1.50 if weight_oz < 8 else 2.50

    total = cost + packaging_cost

    result = f"📦 SHIPPING COST BREAKDOWN ({carrier} {service_type})
"
    result += f"Weight: {weight_oz}oz ({weight_lb:.2f}lb)
"
    result += f"Destination: {destination.title()}
"
    result += f"Service: {service_type}
"
    result += f"{'='*30}
"
    result += f"Base Shipping:  ${cost:.2f}
"
    result += f"Packaging:      ${packaging_cost:.2f}
"
    result += f"{'='*30}
"
    result += f"Total:          ${total:.2f}

"

    # Compare with other carriers
    result += "💡 PRICE COMPARISON:
"
    for c in ["USPS", "UPS", "FedEx"]:
        if c != carrier:
            alt_rates = SHIPPING_RATES.get(c, {})
            alt_service = list(alt_rates.keys())[0] if alt_rates else "Ground"
            alt_cost = list(alt_rates.get(alt_service, {}).values())[-1] if alt_rates.get(alt_service) else 0
            result += f"  {c} ({alt_service}): ~${alt_cost + packaging_cost:.2f}
"

    return result

@tool
def create_order(
    customer_name: str,
    items: str,  # JSON string of items
    shipping_address: str,
    weight_oz: float,
    carrier: str = "USPS",
    service_type: str = "First Class"
) -> str:
    """Create a new order record.

    Args:
        customer_name: Customer name
        items: JSON string of items [{"item_id": "...", "quantity": 1, "price": 15.00}]
        shipping_address: Shipping address
        weight_oz: Total package weight in ounces
        carrier: Selected carrier
        service_type: Selected service type

    Returns:
        Order confirmation with shipping cost
    """
    os.makedirs(os.path.dirname(ORDERS_FILE), exist_ok=True)

    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {"orders": []}

    import json as json_mod
    order_items = json_mod.loads(items)

    subtotal = sum(item["price"] * item["quantity"] for item in order_items)

    # Calculate shipping
    carrier_rates = SHIPPING_RATES.get(carrier, SHIPPING_RATES["USPS"])
    service_rates = carrier_rates.get(service_type, list(carrier_rates.values())[0])
    shipping_cost = list(service_rates.values())[-1]  # Simplified

    # Free shipping threshold
    free_shipping_threshold = 35.0
    if subtotal >= free_shipping_threshold:
        shipping_cost = 0.0
        shipping_note = "FREE (order over $35)"
    else:
        shipping_note = f"${shipping_cost:.2f}"

    total = subtotal + shipping_cost

    order_id = f"ORD-{len(data['orders']) + 1:05d}"

    order = {
        "order_id": order_id,
        "customer_name": customer_name,
        "items": order_items,
        "shipping_address": shipping_address,
        "weight_oz": weight_oz,
        "carrier": carrier,
        "service_type": service_type,
        "subtotal": subtotal,
        "shipping_cost": shipping_cost,
        "total": total,
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }

    data["orders"].append(order)

    with open(ORDERS_FILE, "w") as f:
        json_mod.dump(data, f, indent=2)

    result = f"🎉 ORDER CREATED: {order_id}
"
    result += f"Customer: {customer_name}
"
    result += f"Items:
"
    for item in order_items:
        result += f"  • {item.get('name', item['item_id'])} x{item['quantity']} = ${item['price'] * item['quantity']:.2f}
"
    result += f"Subtotal: ${subtotal:.2f}
"
    result += f"Shipping: {shipping_note}
"
    result += f"Total: ${total:.2f}
"
    result += f"Carrier: {carrier} {service_type}
"
    result += f"Status: Pending fulfillment"

    return result

@tool
def get_packaging_recommendation(item_types: str, fragile: bool = False) -> str:
    """Get packaging recommendations for items.

    Args:
        item_types: Comma-separated list of item types (jewelry, crochet, bookmark, keychain)
        fragile: Whether items are fragile

    Returns:
        Packaging recommendation
    """
    items = [i.strip().lower() for i in item_types.split(",")]

    recommendations = []
    total_weight = 0

    for item in items:
        if item == "jewelry":
            recommendations.append("📿 Jewelry: Anti-tarnish pouch + bubble mailer (add tissue paper for presentation)")
            total_weight += 1.5
        elif item == "crochet":
            recommendations.append("🧶 Crochet: Cellophane bag + kraft box (keeps shape, looks gift-ready)")
            total_weight += 2.0
        elif item == "bookmark":
            recommendations.append("📖 Bookmark: Cardboard backing + cello sleeve (prevents bending)")
            total_weight += 0.5
        elif item == "keychain":
            recommendations.append("🔑 Keychain: Small organza bag + bubble mailer")
            total_weight += 1.0
        else:
            recommendations.append(f"🎁 {item.title()}: Standard bubble mailer")
            total_weight += 1.5

    if fragile:
        recommendations.append("⚠️ FRAGILE: Add 'FRAGILE' sticker + extra bubble wrap layer")
        total_weight += 1.0

    result = "📦 PACKAGING RECOMMENDATIONS
"
    result += "=" * 40 + "
"
    for rec in recommendations:
        result += f"{rec}
"

    result += f"
Estimated packaging weight: {total_weight:.1f}oz
"
    result += "
💡 Eco-friendly tip: Consider recycled kraft mailers and biodegradable packing peanuts! 🌿"

    return result

@tool
def get_order_status(order_id: str) -> str:
    """Check the status of an order.

    Args:
        order_id: Order ID to check

    Returns:
        Order status information
    """
    if not os.path.exists(ORDERS_FILE):
        return "No orders found."

    with open(ORDERS_FILE, "r") as f:
        data = json.load(f)

    for order in data["orders"]:
        if order["order_id"] == order_id:
            result = f"📋 ORDER STATUS: {order_id}
"
            result += f"Customer: {order['customer_name']}
"
            result += f"Status: {order['status'].upper()}
"
            result += f"Total: ${order['total']:.2f}
"
            result += f"Carrier: {order['carrier']} {order['service_type']}
"
            result += f"Created: {order['created_at'][:10]}
"
            return result

    return f"Order {order_id} not found."
