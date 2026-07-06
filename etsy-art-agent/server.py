#!/usr/bin/env python3
"""Etsy Art Agent - Python API & Static File Server.

Exposes REST APIs for inventory, shipping, customers, and reminders,
and implements a live Gemini AI Chatbot route. Serves the web interface locally.
"""

import os
import sys
import json
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Import security and tools
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from etsy_business_manager.utils.security import verify_api_key, validate_safe_path, sanitize_input
from etsy_business_manager.tools.inventory_tools import get_inventory, update_stock, add_inventory_item, get_profit_analysis
from etsy_business_manager.tools.shipping_tools import calculate_shipping_cost, get_packaging_recommendation
from etsy_business_manager.tools.marketing_tools import generate_instagram_caption
from etsy_business_manager.tools.reminder_tools import set_reminder

# Try to import Gemini SDK if installed
HAS_GEMINI_SDK = False
try:
    import google.generativeai as genai
    HAS_GEMINI_SDK = True
except ImportError:
    pass

class EtsyAPIRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Allow CORS
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200, "OK")
        self.end_headers()

    def do_GET(self):
        # API Routes
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path == "/api/inventory":
            self.send_json_file("inventory.json")
        elif path == "/api/customers":
            self.send_customers_data()
        elif path == "/api/reminders":
            self.send_json_file("reminders.json")
        elif path == "/api/orders":
            self.send_json_file("orders.json")
        elif path == "/api/calendar":
            self.send_json_file("content_calendar.json")
        else:
            # Fall back to serving static files from web_interface/
            # Modify path to look inside web_interface/
            if self.path == "/" or self.path == "":
                self.path = "/index.html"
            
            # Prevent directory traversal
            clean_path = self.path.lstrip('/')
            safe_target = os.path.abspath(os.path.join("web_interface", clean_path))
            web_interface_abs = os.path.abspath("web_interface")
            
            if not safe_target.startswith(web_interface_abs):
                self.send_error(403, "Access Denied")
                return
                
            # If serving static files, override path to local file path
            original_cwd = os.getcwd()
            try:
                os.chdir("web_interface")
                self.path = "/" + clean_path
                super().do_GET()
            finally:
                os.chdir(original_cwd)

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        # Read POST body
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            body = json.loads(post_data) if post_data else {}
        except json.JSONDecodeError:
            body = {}

        if path == "/api/chat":
            self.handle_chat_api(body)
        elif path == "/api/inventory/update":
            self.handle_inventory_update(body)
        elif path == "/api/inventory/add":
            self.handle_inventory_add(body)
        elif path == "/api/customers/log":
            self.handle_customer_log(body)
        elif path == "/api/reminders/add":
            self.handle_reminder_add(body)
        elif path == "/api/reminders/toggle":
            self.handle_reminder_toggle(body)
        elif path == "/api/orders/update_status":
            self.handle_order_status_update(body)
        elif path == "/api/shipping/calculate":
            self.handle_shipping_calculate(body)
        elif path == "/api/marketing/generate":
            self.handle_marketing_generate(body)
        else:
            self.send_error(404, "Endpoint not found")

    # --- Helper methods ---

    def send_json_file(self, filename):
        try:
            safe_path = validate_safe_path(filename)
        except PermissionError:
            self.send_error(403, "Sandbox violation")
            return

        if not os.path.exists(safe_path):
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"items": [], "error": "File not found"}')
            return

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        with open(safe_path, 'rb') as f:
            self.wfile.write(f.read())

    def send_customers_data(self):
        # Returns clients combined with messages log
        try:
            clients_path = validate_safe_path("clients.json")
            messages_path = validate_safe_path("messages.json")
        except PermissionError:
            self.send_error(403, "Sandbox violation")
            return

        clients_data = {"clients": []}
        messages_data = {"messages": []}

        if os.path.exists(clients_path):
            with open(clients_path, 'r') as f:
                clients_data = json.load(f)
        if os.path.exists(messages_path):
            with open(messages_path, 'r') as f:
                messages_data = json.load(f)

        response = {
            "clients": clients_data.get("clients", []),
            "messages": messages_data.get("messages", [])
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))

    # --- API Handlers ---

    def handle_chat_api(self, body):
        prompt = sanitize_input(body.get("prompt", ""))
        if not prompt:
            self.send_json_response({"error": "Empty prompt"}, 400)
            return

        # Check API Key
        has_key = verify_api_key()
        
        # Determine Routing Intent (Multi-Agent Coordinator)
        lower_prompt = prompt.lower()
        agent_delegated = "Root Coordinator"
        tools_executed = []
        context_data = ""

        # Routing rules & tool collection
        if any(w in lower_prompt for w in ["inventory", "stock", "product", "left", "many"]):
            agent_delegated = "inventory_manager"
            try:
                context_data = get_inventory()
                tools_executed.append("get_inventory")
                if "profit" in lower_prompt or "margin" in lower_prompt:
                    context_data += "\n" + get_profit_analysis()
                    tools_executed.append("get_profit_analysis")
            except Exception as e:
                context_data = f"Error fetching inventory context: {e}"

        elif any(w in lower_prompt for w in ["instagram", "caption", "post", "social", "hashtag"]):
            agent_delegated = "marketing_manager"
            # Extract product metadata if possible
            prod_name = "Ocean Wave Crochet Bookmark"
            prod_type = "crochet"
            if "keychain" in lower_prompt:
                prod_name = "Resin Pressed Flower Keychain"
                prod_type = "keychain"
            elif "pendant" in lower_prompt or "jewelry" in lower_prompt:
                prod_name = "Wire Wrap Moonstone Pendant"
                prod_type = "jewelry"
            elif "bear" in lower_prompt:
                prod_name = "Amigurumi Cozy Bear Plush"
                prod_type = "crochet"

            try:
                caption = generate_instagram_caption(product_name=prod_name, product_type=prod_type)
                context_data = f"Suggested Instagram Post:\n{caption}"
                tools_executed.append("generate_instagram_caption")
            except Exception as e:
                context_data = f"Error creating caption: {e}"

        elif any(w in lower_prompt for w in ["shipping", "cost", "usps", "carrier", "deliver", "package"]):
            agent_delegated = "shipping_manager"
            try:
                # Mock average parcel weight (5oz)
                shipping_rates = calculate_shipping_cost(weight_oz=5.0, carrier="USPS", service_type="First Class")
                pkg_advice = get_packaging_recommendation("bookmarks")
                context_data = f"Shipping Details:\n{shipping_rates}\nPackaging Guidance: {pkg_advice}"
                tools_executed.append("calculate_shipping_cost")
            except Exception as e:
                context_data = f"Error computing shipping rates: {e}"

        elif any(w in lower_prompt for w in ["customer", "message", "reply", "email", "client"]):
            agent_delegated = "client_communication_manager"
            try:
                clients_path = validate_safe_path("clients.json")
                if os.path.exists(clients_path):
                    with open(clients_path, 'r') as f:
                        clients = json.load(f).get("clients", [])
                    context_data = f"Customer List:\n{json.dumps(clients, indent=2)}"
                tools_executed.append("get_customer_history")
            except Exception as e:
                context_data = f"Error loading customer details: {e}"

        elif any(w in lower_prompt for w in ["reminder", "todo", "calendar", "task", "deadline", "fair"]):
            agent_delegated = "reminder_manager"
            try:
                reminders_path = validate_safe_path("reminders.json")
                if os.path.exists(reminders_path):
                    with open(reminders_path, 'r') as f:
                        reminders = json.load(f).get("reminders", [])
                    context_data = f"Reminders Board:\n{json.dumps(reminders, indent=2)}"
                tools_executed.append("get_upcoming_reminders")
            except Exception as e:
                context_data = f"Error loading task scheduler: {e}"

        # Generate Response using Gemini API if key is present
        ai_response_text = ""
        if has_key and HAS_GEMINI_SDK:
            try:
                genai.configure(api_key=os.environ["GEMINI_API_KEY"])
                model = genai.GenerativeModel("gemini-2.5-flash")
                
                system_instruction = f"""You are the Etsy Business Manager AI chatbot.
You help the user navigate their business. When appropriate, you delegate to sub-agents.
Currently delegated: **{agent_delegated}**.
Tools executed: {tools_executed}.
Available local database context:
{context_data}

Acknowledge your delegated agent and tools. Keep responses conversational, professional, and directly address the user query using the database details. Do NOT mention details about Python variables or JSON paths.
"""
                chat = model.start_chat()
                response = chat.send_message(f"{system_instruction}\n\nUser request: {prompt}")
                ai_response_text = response.text
            except Exception as e:
                ai_response_text = f"⚠️ Gemini API Call Failed: {e}. Falling back to offline assistant logic."
                
        # Offline/Mock fallback if Gemini SDK not loaded or key is missing
        if not ai_response_text:
            if not has_key:
                warning_banner = "\n\n⚠️ *[Offline Mode: GEMINI_API_KEY is not set. Showing simulated agent coordination response. To enable full AI, set your GEMINI_API_KEY environment variable.]*"
            else:
                warning_banner = "\n\n⚠️ *[Offline Mode: google-generativeai SDK import issue. Showing offline assistant response.]*"

            if agent_delegated == "inventory_manager":
                ai_response_text = f"I've delegated your request to the **inventory_manager**. I found 4 active products. Amigurumi Cozy Bear Plush is running critical (stock: 2). Would you like to check profit margins or increment stock?" + warning_banner
            elif agent_delegated == "marketing_manager":
                ai_response_text = f"I've delegated your query to the **marketing_manager** to draft an Instagram post. Here's a draft caption:\n\n'There's something so special about handmade crochet... 💕'\n\nWould you like to schedule this to the content calendar?" + warning_banner
            elif agent_delegated == "shipping_manager":
                ai_response_text = f"Delegated to the **shipping_manager**. Domestic shipping for a standard 5oz parcel via USPS First Class is calculated at $5.50. I recommend utilizing bubble mailers to avoid shipping damage." + warning_banner
            elif agent_delegated == "client_communication_manager":
                ai_response_text = f"Delegated to the **client_communication_manager**. I found inquiries from Sarah Miller (Custom Koala plush request) and Michael Taylor (shipping date inquiry). Would you like me to draft auto-replies?" + warning_banner
            elif agent_delegated == "reminder_manager":
                ai_response_text = f"Delegated to the **reminder_manager**. You have 4 pending reminders including: Q2 tax filing (Jul 15) and restocking bear materials (Jul 09)." + warning_banner
            else:
                ai_response_text = f"Welcome! I am your Etsy Business Manager orchestrator agent. I can coordinate with the inventory, marketing, shipping, customer support, and task reminder sub-agents. How can I help you today?" + warning_banner

        self.send_json_response({
            "response": ai_response_text,
            "metadata": {
                "delegated_agent": agent_delegated,
                "tools_used": tools_executed,
                "api_connected": has_key
            }
        })

    def handle_inventory_update(self, body):
        item_id = body.get("item_id")
        quantity_change = int(body.get("quantity_change", 0))
        
        try:
            res = update_stock(item_id=item_id, quantity_change=quantity_change)
            self.send_json_response({"message": res})
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)

    def handle_inventory_add(self, body):
        name = body.get("name")
        category = body.get("category")
        description = body.get("description", "")
        quantity = int(body.get("quantity", 0))
        material_cost = float(body.get("material_cost", 0.0))
        selling_price = float(body.get("selling_price", 0.0))
        materials_used = body.get("materials_used", [])
        time_to_make = int(body.get("time_to_make_minutes", 0))
        tags = body.get("tags", [])

        try:
            res = add_inventory_item(
                name=name, category=category, description=description, quantity=quantity,
                material_cost=material_cost, selling_price=selling_price,
                materials_used=materials_used, time_to_make_minutes=time_to_make, tags=tags
            )
            self.send_json_response({"message": res})
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)

    def handle_customer_log(self, body):
        client_name = body.get("name")
        channel = body.get("channel", "Email")
        content = body.get("content")
        
        try:
            clients_path = validate_safe_path("clients.json")
            messages_path = validate_safe_path("messages.json")
            
            # Read and update clients
            with open(clients_path, 'r') as f:
                c_data = json.load(f)
            
            client_id = None
            for c in c_data["clients"]:
                if c["name"].lower() == client_name.lower():
                    client_id = c["client_id"]
                    c["last_interaction"] = datetime_now_iso()
                    c["total_orders"] = c.get("total_orders", 0) + 1
                    break
                    
            if not client_id:
                client_id = f"CL-{len(c_data['clients']) + 1:04d}"
                c_data["clients"].append({
                    "client_id": client_id,
                    "name": client_name,
                    "email": f"{client_name.lower().replace(' ', '.')}@example.com",
                    "phone": "555-0100",
                    "tags": ["new logger"],
                    "total_orders": 1,
                    "last_interaction": datetime_now_iso(),
                    "note": "Logged automatically via chat interface."
                })
                
            with open(clients_path, 'w') as f:
                json.dump(c_data, f, indent=2)

            # Read and update message logs
            with open(messages_path, 'r') as f:
                m_data = json.load(f)
                
            msg_id = f"MSG-{len(m_data['messages']) + 1:04d}"
            m_data["messages"].append({
                "message_id": msg_id,
                "client_id": client_id,
                "timestamp": datetime_now_iso(),
                "channel": channel,
                "direction": "incoming",
                "content": content,
                "resolved": False
            })
            
            with open(messages_path, 'w') as f:
                json.dump(m_data, f, indent=2)
                
            self.send_json_response({"message": "✅ Customer interaction successfully logged!"})
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)

    def handle_reminder_add(self, body):
        title = body.get("title")
        category = body.get("category", "Urgent")
        due_date = body.get("due_date")
        notes = body.get("notes", "")

        try:
            reminders_path = validate_safe_path("reminders.json")
            with open(reminders_path, 'r') as f:
                data = json.load(f)

            rem_id = f"REM-{len(data['reminders']) + 1:04d}"
            data["reminders"].append({
                "reminder_id": rem_id,
                "title": title,
                "category": category,
                "due_date": due_date,
                "status": "pending",
                "notes": notes
            })

            with open(reminders_path, 'w') as f:
                json.dump(data, f, indent=2)

            self.send_json_response({"message": f"✅ Reminder Scheduled! (ID: {rem_id})"})
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)

    def handle_reminder_toggle(self, body):
        reminder_id = body.get("reminder_id")

        try:
            reminders_path = validate_safe_path("reminders.json")
            with open(reminders_path, 'r') as f:
                data = json.load(f)

            found = False
            for rem in data["reminders"]:
                if rem["reminder_id"] == reminder_id:
                    rem["status"] = "completed" if rem["status"] == "pending" else "pending"
                    found = True
                    break

            if found:
                with open(reminders_path, 'w') as f:
                    json.dump(data, f, indent=2)
                self.send_json_response({"message": "✅ Reminder updated!"})
            else:
                self.send_json_response({"error": "Reminder not found"}, 404)
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)

    def handle_order_status_update(self, body):
        order_id = body.get("order_id")
        new_status = body.get("status")

        try:
            orders_path = validate_safe_path("orders.json")
            with open(orders_path, 'r') as f:
                data = json.load(f)

            found = False
            for order in data["orders"]:
                if order["order_id"] == order_id:
                    order["status"] = new_status
                    found = True
                    break

            if found:
                with open(orders_path, 'w') as f:
                    json.dump(data, f, indent=2)
                self.send_json_response({"message": f"✅ Order {order_id} pipeline updated to {new_status}!"})
            else:
                self.send_json_response({"error": "Order not found"}, 404)
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)

    def handle_shipping_calculate(self, body):
        weight = float(body.get("weight_oz", 5.0))
        carrier = body.get("carrier", "USPS")
        service = body.get("service_type", "First Class")
        dest = body.get("destination", "domestic")
        package_type = body.get("package_type", "standard")

        try:
            rate_string = calculate_shipping_cost(
                weight_oz=weight, carrier=carrier, service_type=service,
                destination=dest, package_type=package_type
            )
            pkg_advice = get_packaging_recommendation(package_type)
            self.send_json_response({
                "rate": rate_string,
                "recommendation": pkg_advice
            })
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)

    def handle_marketing_generate(self, body):
        product_name = body.get("product_name")
        product_type = body.get("product_type")
        mood = body.get("mood", "warm")

        try:
            caption = generate_instagram_caption(
                product_name=product_name, product_type=product_type, mood=mood
            )
            self.send_json_response({"caption": caption})
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)

    def send_json_response(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

def datetime_now_iso():
    from datetime import datetime
    return datetime.now().isoformat()

def run_server(port=8080):
    # Reconfigure stdout to use utf-8 if supported on this platform
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
    server_address = ('', port)
    httpd = HTTPServer(server_address, EtsyAPIRequestHandler)
    print(f"[SERVER] Etsy Business Manager Backend & UI Server running at http://localhost:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[SERVER] Stopping server...")
        httpd.server_close()

if __name__ == '__main__':
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    run_server(port)
