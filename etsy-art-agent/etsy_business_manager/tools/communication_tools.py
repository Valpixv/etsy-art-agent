"""Client communication and customer service tools.

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

CLIENTS_FILE = "etsy_business_manager/data/clients.json"
MESSAGES_FILE = "etsy_business_manager/data/messages.json"

@tool
def draft_response(
    customer_name: str,
    inquiry_type: str,
    product_name: Optional[str] = None,
    tone: str = "friendly_professional",
    specific_details: str = ""
) -> str:
    """Draft a professional customer response.

    Args:
        customer_name: Customer's name
        inquiry_type: Type of inquiry (order_status, custom_request, shipping_question, return_request, general_inquiry, review_thanks)
        product_name: Optional product they're asking about
        tone: Communication tone (friendly_professional, warm, formal, casual)
        specific_details: Any specific details to include in the response

    Returns:
        Drafted response message
    """

    # Tone modifiers
    tone_prefixes = {
        "friendly_professional": "Hi",
        "warm": "Hey there",
        "formal": "Dear",
        "casual": "Hi"
    }

    # Response templates using triple quotes for multi-line safety
    templates = {
        "order_status": {
            "friendly_professional": f"""Hi {customer_name}!

Thank you so much for reaching out about your order. I wanted to let you know that your package is currently being prepared with care and will be shipped within 1-2 business days. You'll receive a tracking notification as soon as it's on its way!

If you have any other questions, I'm always happy to help. 💕

Best regards""",
            "warm": f"""Hey {customer_name}!

Just wanted to give you a quick update — your order is being handmade with lots of love right now! I'll have it shipped out in the next day or two and will send you tracking info as soon as it's on its way. Thanks for being so patient! 🌸

Xoxo""",
            "formal": f"""Dear {customer_name},

Thank you for your inquiry regarding your order status. Please be advised that your order is currently in the production phase and will be dispatched within 1-2 business days. You will receive tracking information via email upon shipment.

Should you require further assistance, please do not hesitate to contact us.

Sincerely""",
            "casual": f"""Hi {customer_name}!

Your order is in progress! I'm working on it now and will ship it out soon. You'll get tracking info when it goes out. Thanks for shopping with me! ✨"""
        },
        "custom_request": {
            "friendly_professional": f"""Hi {customer_name}!

Thank you for your interest in a custom piece! I absolutely love creating personalized items. Based on what you've shared, here's what I can do:

{specific_details}

Custom orders typically take 3-5 business days to create, and I'll send you photos for approval before shipping. Let me know if you'd like to proceed!

Best regards""",
            "warm": f"""Hey {customer_name}!

I'm so excited about your custom request! 🎨 Here's what I'm thinking:

{specific_details}

I'll make sure to send you progress pics so you can see it come to life. Custom pieces usually take about 3-5 days. Sound good?

Can't wait to create something special for you! 💕""",
            "formal": f"""Dear {customer_name},

Thank you for your custom order inquiry. We would be pleased to accommodate your request.

{specific_details}

Please note that custom orders require 3-5 business days for production. We will provide photographic confirmation prior to dispatch.

Kindly confirm your acceptance to proceed.

Sincerely""",
            "casual": f"""Hi {customer_name}!

Love your custom idea! 🌈 Here's the plan:

{specific_details}

Takes about 3-5 days to make. I'll show you pics before I ship! Let me know if you want to move forward. ✨"""
        },
        "shipping_question": {
            "friendly_professional": f"""Hi {customer_name}!

Great question about shipping! Here's the info:

{specific_details}

All orders are carefully packaged to ensure they arrive safely. I typically ship via USPS First Class (2-5 business days domestically) or Priority if you need it faster.

International shipping is available too — just let me know your location and I'll get you an accurate quote!

Best regards""",
            "warm": f"""Hey {customer_name}!

{specific_details}

I pack everything super carefully so your handmade goodies arrive in perfect condition! 🎁 Usually ships USPS First Class (2-5 days in the US). Need it faster? I can do Priority!

Also ship internationally — just tell me where and I'll figure out the best rate for you. 🌍

Thanks!""",
            "formal": f"""Dear {customer_name},

Regarding your shipping inquiry:

{specific_details}

All items are securely packaged for transit. Standard domestic shipping is via USPS First Class (estimated 2-5 business days). Expedited shipping options are available upon request.

International shipping is available; please provide your destination country for an accurate quotation.

Sincerely""",
            "casual": f"""Hi {customer_name}!

{specific_details}

I ship USPS First Class (2-5 days US). Pack everything super safe! Can do faster shipping if you need. Also ship worldwide — where are you located? 🌎"""
        },
        "return_request": {
            "friendly_professional": f"""Hi {customer_name},

I'm sorry to hear that your order didn't meet your expectations. Your satisfaction is really important to me.

{specific_details}

I accept returns within 14 days of delivery. Please ensure the item is in its original condition. Once I receive the return, I'll process your refund within 2-3 business days.

I'd also love to know what went wrong so I can improve — your feedback means a lot!

Best regards""",
            "warm": f"""Hey {customer_name},

I'm really sorry things didn't work out. 💔 {specific_details}

You can return within 14 days — just send it back in good condition and I'll refund you as soon as I get it. No stress!

Also, if you're comfortable sharing what happened, I'd really appreciate it so I can do better next time.

Thanks for giving my shop a try!""",
            "formal": f"""Dear {customer_name},

We regret that your purchase did not meet your expectations.

{specific_details}

Returns are accepted within 14 days of delivery, provided the item remains in its original condition. Refunds will be processed within 2-3 business days of receipt.

We would greatly appreciate any feedback regarding your experience to help us improve our products and service.

Sincerely""",
            "casual": f"""Hi {customer_name},

Bummer that it didn't work out! 😕 {specific_details}

Return within 14 days and I'll refund you once I get it back. Easy! Would love to know what happened so I can fix it for next time."""
        },
        "general_inquiry": {
            "friendly_professional": f"""Hi {customer_name}!

Thank you for getting in touch! {specific_details}

I'm always happy to answer questions about my handmade pieces. Feel free to ask anything else — I'm here to help!

Best regards""",
            "warm": f"""Hey {customer_name}!

{specific_details}

Thanks for reaching out! I love chatting about my work, so ask away if you have more questions! 💕""",
            "formal": f"""Dear {customer_name},

Thank you for your inquiry. {specific_details}

Please do not hesitate to contact us should you require any further information.

Sincerely""",
            "casual": f"""Hi {customer_name}!

{specific_details}

No worries at all — happy to help! Hit me up if you need anything else. ✨"""
        },
        "review_thanks": {
            "friendly_professional": f"""Hi {customer_name}!

I just saw your review and wanted to say a huge thank you! 💕 It means the world to me when customers take the time to share their experience. I'm so glad you love your {product_name or 'purchase'}!

Your support helps my small business grow, and I truly appreciate it. Hope to see you again soon!

Best regards""",
            "warm": f"""Hey {customer_name}!

OMG your review made my day! 🌸 Thank you SO much for the kind words about your {product_name or 'purchase'}. I put so much love into every piece and it means everything to know you love it!

You're the best — come back anytime! 💕""",
            "formal": f"""Dear {customer_name},

We wish to express our sincere gratitude for your positive review. We are delighted that you are satisfied with your {product_name or 'purchase'}.

Your feedback is invaluable to our continued growth and improvement. We look forward to serving you again in the future.

Sincerely""",
            "casual": f"""Hi {customer_name}!

Thanks for the awesome review! 🎉 So glad you love your {product_name or 'purchase'}! Means a lot to a small shop like mine. Come back soon! ✨"""
        }
    }

    response = templates.get(inquiry_type, templates["general_inquiry"]).get(tone, templates["general_inquiry"]["friendly_professional"])
    return response

@tool
def log_customer_interaction(
    customer_name: str,
    interaction_type: str,
    notes: str,
    order_id: Optional[str] = None
) -> str:
    """Log a customer interaction for future reference.

    Args:
        customer_name: Customer name
        interaction_type: Type of interaction (inquiry, order, complaint, compliment, custom_request)
        notes: Notes about the interaction
        order_id: Optional associated order ID

    Returns:
        Confirmation of logged interaction
    """
    os.makedirs(os.path.dirname(MESSAGES_FILE), exist_ok=True)

    if os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {"interactions": []}

    interaction = {
        "id": f"INT-{len(data['interactions']) + 1:04d}",
        "customer_name": customer_name,
        "interaction_type": interaction_type,
        "notes": notes,
        "order_id": order_id,
        "timestamp": datetime.now().isoformat()
    }

    data["interactions"].append(interaction)

    with open(MESSAGES_FILE, "w") as f:
        json.dump(data, f, indent=2)

    return f"📝 Logged {interaction_type} from {customer_name} (ID: {interaction['id']})"

@tool
def get_customer_history(customer_name: str) -> str:
    """Retrieve interaction history for a customer.

    Args:
        customer_name: Customer name to look up

    Returns:
        Customer interaction history
    """
    if not os.path.exists(MESSAGES_FILE):
        return f"No history found for {customer_name}."

    with open(MESSAGES_FILE, "r") as f:
        data = json.load(f)

    interactions = [
        i for i in data["interactions"]
        if i["customer_name"].lower() == customer_name.lower()
    ]

    if not interactions:
        return f"No history found for {customer_name}."

    result = f"📋 CUSTOMER HISTORY: {customer_name}\n"
    result += "=" * 40 + "\n"

    for i in interactions:
        result += f"\n[{i['timestamp'][:10]}] {i['interaction_type'].upper()}\n"
        result += f"  {i['notes']}\n"
        if i['order_id']:
            result += f"  Order: {i['order_id']}\n"

    return result
