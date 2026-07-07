#!/usr/bin/env python3
"""Model Context Protocol (MCP) Server for the Etsy Art Business Manager.

Exposes inventory, shipping, marketing, and reminder tools over stdio JSON-RPC.
This file implements standard MCP JSON-RPC protocol to allow integration with LLM clients.
"""

import json
import sys
import os

# Import tools from business manager
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from etsy_business_manager.tools.inventory_tools import get_inventory, add_inventory_item, update_stock, check_low_stock, get_profit_analysis
from etsy_business_manager.tools.shipping_tools import calculate_shipping_cost
from etsy_business_manager.tools.marketing_tools import generate_instagram_caption
from etsy_business_manager.tools.reminder_tools import set_reminder

def log(msg):
    sys.stderr.write(f"[MCP LOG] {msg}\n")
    sys.stderr.flush()

def handle_tools_list():
    return {
        "tools": [
            {
                "name": "get_inventory",
                "description": "Fetch list of handmade items. Optionally filter by category.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "category": {"type": "string", "description": "Optional category filter: crochet, jewelry, keychains, bookmarks"}
                    }
                }
            },
            {
                "name": "update_stock",
                "description": "Adjust stock quantity for an item (positive to add, negative to subtract).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "item_id": {"type": "string", "description": "Product ID, e.g., CR-0001"},
                        "quantity_change": {"type": "integer", "description": "Amount to change stock by"}
                    },
                    "required": ["item_id", "quantity_change"]
                }
            },
            {
                "name": "calculate_shipping_cost",
                "description": "Calculate USPS/UPS/FedEx domestic or international shipping rates.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "weight_oz": {"type": "number", "description": "Package weight in ounces"},
                        "carrier": {"type": "string", "description": "USPS, UPS, or FedEx"},
                        "service_type": {"type": "string", "description": "e.g., First Class, Ground, Priority"},
                        "destination": {"type": "string", "description": "domestic or international"}
                    },
                    "required": ["weight_oz"]
                }
            },
            {
                "name": "generate_instagram_caption",
                "description": "Create an engaging caption for a handmade product.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "product_name": {"type": "string", "description": "Name of product"},
                        "product_type": {"type": "string", "description": "crochet, jewelry, keychain, bookmark"},
                        "mood": {"type": "string", "description": "warm, playful, elegant, cozy, minimalist"}
                    },
                    "required": ["product_name", "product_type"]
                }
            }
        ]
    }

def handle_tools_call(name, arguments):
    log(f"Calling tool: {name} with args: {arguments}")
    try:
        if name == "get_inventory":
            cat = arguments.get("category")
            res = get_inventory(category=cat)
        elif name == "update_stock":
            iid = arguments.get("item_id")
            change = int(arguments.get("quantity_change", 0))
            res = update_stock(item_id=iid, quantity_change=change)
        elif name == "calculate_shipping_cost":
            weight = float(arguments.get("weight_oz"))
            carrier = arguments.get("carrier", "USPS")
            service = arguments.get("service_type", "First Class")
            dest = arguments.get("destination", "domestic")
            res = calculate_shipping_cost(weight_oz=weight, carrier=carrier, service_type=service, destination=dest)
        elif name == "generate_instagram_caption":
            pname = arguments.get("product_name")
            ptype = arguments.get("product_type")
            mood = arguments.get("mood", "warm")
            res = generate_instagram_caption(product_name=pname, product_type=ptype, mood=mood)
        else:
            return {"isError": True, "content": [{"type": "text", "text": f"Tool '{name}' not found."}]}

        return {
            "content": [
                {
                    "type": "text",
                    "text": str(res)
                }
            ]
        }
    except Exception as e:
        return {
            "isError": True,
            "content": [
                {
                    "type": "text",
                    "text": f"Error executing tool: {str(e)}"
                }
            ]
        }

def main():
    log("Etsy Art MCP Server starting stdio JSON-RPC loop...")
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line)
            method = req.get("method")
            rid = req.get("id")

            if method == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": rid,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "etsy-art-mcp", "version": "1.0.0"}
                    }
                }
            elif method == "tools/list":
                resp = {
                    "jsonrpc": "2.0",
                    "id": rid,
                    "result": handle_tools_list()
                }
            elif method == "tools/call":
                params = req.get("params", {})
                name = params.get("name")
                args = params.get("arguments", {})
                resp = {
                    "jsonrpc": "2.0",
                    "id": rid,
                    "result": handle_tools_call(name, args)
                }
            else:
                resp = {
                    "jsonrpc": "2.0",
                    "id": rid,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
            
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            log(f"Error handling request line: {e}")

if __name__ == "__main__":
    main()
