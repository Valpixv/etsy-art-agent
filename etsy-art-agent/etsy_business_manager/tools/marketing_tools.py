"""Marketing and Instagram content generation tools."""

import json
import os
from datetime import datetime
from typing import List, Optional

try:
    from google.adk.tools import tool
except ImportError:
    def tool(func):
        return func

CONTENT_CALENDAR_FILE = "etsy_business_manager/data/content_calendar.json"

@tool
def generate_instagram_caption(
    product_name: str,
    product_type: str,
    mood: str = "warm",
    include_cta: bool = True,
    emoji_level: str = "moderate"
) -> str:
    """Generate an Instagram caption for a handmade product.

    Args:
        product_name: Name of the product
        product_type: Type (keychain, jewelry, crochet, bookmark, etc.)
        mood: Tone mood (warm, playful, elegant, cozy, minimalist)
        include_cta: Whether to include a call-to-action
        emoji_level: Emoji density (minimal, moderate, heavy)

    Returns:
        Generated caption text
    """

    # Mood-based opening lines
    openings = {
        "warm": [
            f"There's something so special about handmade {product_type}s... 💕",
            f"Made with love, just for you. 🌸",
            f"Every stitch tells a story. ✨",
        ],
        "playful": [
            f"Obsessed with this {product_name}! 🎉",
            f"Your new favorite {product_type} just dropped! 🚀",
            f"Who says handmade can't be fun? 🌈",
        ],
        "elegant": [
            f"Timeless beauty in every detail. 🕊️",
            f"Crafted for those who appreciate the finer things. 💎",
            f"Elegance, handmade. ✨",
        ],
        "cozy": [
            f"Cozy vibes only with this {product_name} 🍂",
            f"The perfect companion for your quiet moments. ☕",
            f"Snuggle up with something handmade. 🧶",
        ],
        "minimalist": [
            f"Simple. Beautiful. Handmade.",
            f"Less is more. Especially when it's made by hand.",
            f"Clean lines, warm heart.",
        ]
    }

    # CTA options
    ctas = [
        "✨ Link in bio to shop! ✨",
        "🛍️ Tap the link in our bio to make it yours!",
        "💌 DM us for custom orders!",
        "🏷️ Tag a friend who needs this!",
        "🌿 Which color would you choose? Tell us below!",
    ]

    # Hashtag sets
    hashtag_sets = {
        "keychain": ["#handmadekeychain", "#customkeychain", "#keychainlover", "#accesories"],
        "jewelry": ["#handmadejewelry", "#artisanjewelry", "#jewelrylover", "#handcrafted"],
        "crochet": ["#crochet", "#crochetersofinstagram", "#handmadeplush", "#amigurumi"],
        "bookmark": ["#handmadebookmark", "#booklover", "#readersofinstagram", "#bookish"],
    }

    opening = openings.get(mood, openings["warm"])[hash(product_name) % 3]

    # Build caption
    caption = f"{opening}

"
    caption += f"Introducing the {product_name}! "
    caption += f"Each {product_type} is carefully crafted by hand, "
    caption += f"making every piece truly one-of-a-kind. 🎨

"
    caption += f"Whether you're treating yourself or looking for the perfect gift, "
    caption += f"this {product_type} brings a personal touch that mass-produced items simply can't match. 💝

"

    if include_cta:
        caption += f"{ctas[hash(product_name) % len(ctas)]}

"

    # Add hashtags
    tags = hashtag_sets.get(product_type.lower(), ["#handmade", "#etsyshop", "#smallbusiness"])
    tags += ["#handmade", "#shopsmall", "#supportsmallbusiness", "#makersgonnamake"]
    tags = list(set(tags))  # Remove duplicates
    caption += " ".join(tags)

    return caption

@tool
def research_hashtags(product_type: str, trend_focus: str = "general") -> str:
    """Research trending hashtags for a product type.

    Args:
        product_type: Type of product (jewelry, crochet, keychains, bookmarks)
        trend_focus: Focus area (general, seasonal, viral, niche)

    Returns:
        Recommended hashtag strategy
    """

    hashtag_db = {
        "keychain": {
            "general": ["#handmadekeychain", "#customkeychain", "#keychain", "#accesories", "#bagcharm"],
            "seasonal": ["#summeraccessories", "#backtoschool", "#giftideas", "#stockingstuffers"],
            "viral": ["#tiktokmademebuyit", "#smallbusinesscheck", "#viralproduct"],
            "niche": ["#resinkeychain", "#embroiderykeychain", "#polymerclay", "#crochetkeychain"]
        },
        "jewelry": {
            "general": ["#handmadejewelry", "#artisanjewelry", "#jewelrydesign", "#handcrafted"],
            "seasonal": ["#summervibes", "#weddingjewelry", "#holidaygifts", "#valentinesday"],
            "viral": ["#tiktokmademebuyit", "#aesthetic", "#trending2026"],
            "niche": ["#wirewrapped", "#beadedjewelry", "#macramejewelry", "#polymerclayjewelry"]
        },
        "crochet": {
            "general": ["#crochet", "#crochetersofinstagram", "#handmadeplush", "#yarnaddict"],
            "seasonal": ["#cozyseason", "#wintercrochet", "#summercrochet", "#holidaycrochet"],
            "viral": ["#crochetok", "#crochetcommunity", "#yarnart"],
            "niche": ["#amigurumi", "#crochetflower", "#crochettoy", "#grannysquare"]
        },
        "bookmark": {
            "general": ["#handmadebookmark", "#booklover", "#readersofinstagram", "#bookish"],
            "seasonal": ["#summerreading", "#backtoschool", "#cozyreading", "#bookclub"],
            "viral": ["#booktok", "#bookstagram", "#aestheticreading"],
            "niche": ["#embroiderybookmark", "#resinbookmark", "#crochetbookmark", "#leatherbookmark"]
        }
    }

    tags = hashtag_db.get(product_type.lower(), {}).get(trend_focus, ["#handmade", "#etsyshop"])

    result = f"📱 HASHTAG STRATEGY FOR {product_type.upper()}
"
    result += f"Focus: {trend_focus}

"
    result += "Recommended hashtags:
"
    for tag in tags:
        result += f"  {tag}
"

    result += "
💡 Tips:
"
    result += "  • Use 20-30 hashtags per post
"
    result += "  • Mix popular (1M+), medium (100K-1M), and niche (<100K) tags
"
    result += "  • Rotate hashtags to avoid looking spammy
"
    result += "  • Create a branded hashtag for your shop
"

    return result

@tool
def schedule_content(
    content_type: str,
    product_name: str,
    scheduled_date: str,
    platform: str = "instagram"
) -> str:
    """Schedule a content piece for social media.

    Args:
        content_type: Type of content (product_showcase, behind_scenes, tutorial, customer_feature)
        product_name: Product to feature
        scheduled_date: Date to post (YYYY-MM-DD)
        platform: Platform (instagram, tiktok, pinterest, facebook)

    Returns:
        Confirmation of scheduled content
    """
    os.makedirs(os.path.dirname(CONTENT_CALENDAR_FILE), exist_ok=True)

    if os.path.exists(CONTENT_CALENDAR_FILE):
        with open(CONTENT_CALENDAR_FILE, "r") as f:
            calendar = json.load(f)
    else:
        calendar = {"posts": []}

    post = {
        "id": f"POST-{len(calendar['posts']) + 1:04d}",
        "content_type": content_type,
        "product_name": product_name,
        "scheduled_date": scheduled_date,
        "platform": platform,
        "status": "scheduled",
        "created_at": datetime.now().isoformat()
    }

    calendar["posts"].append(post)

    with open(CONTENT_CALENDAR_FILE, "w") as f:
        json.dump(calendar, f, indent=2)

    content_emojis = {
        "product_showcase": "📸",
        "behind_scenes": "🎬",
        "tutorial": "🧶",
        "customer_feature": "💝"
    }

    emoji = content_emojis.get(content_type, "📌")
    return f"{emoji} Scheduled '{content_type}' for '{product_name}' on {platform} for {scheduled_date} (ID: {post['id']})"

@tool
def get_content_calendar(days_ahead: int = 7) -> str:
    """Get upcoming scheduled content.

    Args:
        days_ahead: Number of days to look ahead

    Returns:
        Content calendar overview
    """
    if not os.path.exists(CONTENT_CALENDAR_FILE):
        return "📅 No content scheduled yet. Use schedule_content to plan posts!"

    with open(CONTENT_CALENDAR_FILE, "r") as f:
        calendar = json.load(f)

    from datetime import datetime, timedelta
    today = datetime.now().date()
    cutoff = today + timedelta(days=days_ahead)

    upcoming = [
        post for post in calendar["posts"]
        if datetime.strptime(post["scheduled_date"], "%Y-%m-%d").date() <= cutoff
        and post["status"] == "scheduled"
    ]

    if not upcoming:
        return f"📅 No content scheduled for the next {days_ahead} days."

    result = f"📅 CONTENT CALENDAR (Next {days_ahead} Days)
"
    result += "=" * 40 + "
"

    for post in sorted(upcoming, key=lambda x: x["scheduled_date"]):
        result += f"
{post['scheduled_date']} | {post['platform'].upper()}
"
        result += f"  Type: {post['content_type']}
"
        result += f"  Product: {post['product_name']}
"
        result += f"  ID: {post['id']}
"

    return result
