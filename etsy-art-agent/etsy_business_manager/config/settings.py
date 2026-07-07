"""Configuration and constants for the Etsy Business Manager."""

from dataclasses import dataclass
from typing import List

# Business Categories
HANDMADE_CATEGORIES = [
    "keychains",
    "jewelry",
    "crochet",
    "bookmarks",
    "stickers",
    "pottery",
    "embroidery",
    "resin_art",
]

# Shipping Carriers
SHIPPING_CARRIERS = ["USPS", "UPS", "FedEx", "DHL"]

# Instagram Settings
INSTAGRAM_HASHTAG_POOL = [
    "#handmade", "#etsyshop", "#smallbusiness", "#handcrafted",
    "#shopsmall", "#makersgonnamake", "#handmadejewelry",
    "#crochet", "#bookmark", "#keychain", "#artisan",
    "#supportsmallbusiness", "#handmadewithlove", "#craftbusiness",
]

# Inventory Thresholds
LOW_STOCK_THRESHOLD = 5
CRITICAL_STOCK_THRESHOLD = 2

# File paths
DATA_DIR = "etsy_business_manager/data"
INVENTORY_FILE = f"{DATA_DIR}/inventory.json"
CLIENTS_FILE = f"{DATA_DIR}/clients.json"
ORDERS_FILE = f"{DATA_DIR}/orders.json"
REMINDERS_FILE = f"{DATA_DIR}/reminders.json"

@dataclass
class BusinessConfig:
    shop_name: str = "Handmade by You"
    shop_owner: str = "Artist"
    etsy_shop_url: str = ""
    instagram_handle: str = ""
    default_shipping_carrier: str = "USPS"
    business_email: str = ""

    # Pricing defaults
    default_markup_percent: float = 2.5  # 2.5x material cost
    minimum_order_value: float = 5.0
    free_shipping_threshold: float = 35.0

    # Communication tone
    tone_style: str = "friendly_professional"  # friendly_professional, casual, formal

DEFAULT_CONFIG = BusinessConfig()
