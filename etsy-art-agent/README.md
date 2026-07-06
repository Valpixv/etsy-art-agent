# 🎨 Etsy Art Agent — Handmade Business Manager

> **Google 5-Day Capstone Project** | Built with Google's Agent Development Kit (ADK) & Agents CLI

A production-ready multi-agent system designed to help run a handmade art and craft business on Etsy. Specializes in inventory management, Instagram marketing, client communication, shipping cost optimization, and smart reminders.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (fast Python package installer)
- Node.js (for Agents CLI skills)
- Google Cloud project (optional, for deployment)

### 1. Clone & Setup Environment

```bash
git clone https://github.com/YOUR_USERNAME/etsy-art-agent.git
cd etsy-art-agent

# Create virtual environment
python -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Install Agents CLI

```bash
# Using uv (recommended)
uvx google-agents-cli setup

# Or using pip
pip install google-agents-cli
agents-cli setup
```

### 3. Configure Environment Variables

```bash
export GEMINI_API_KEY="your-gemini-api-key"
export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"  # Optional
```

### 4. Run the Agent

```bash
# Terminal mode
adk run etsy_business_manager

# Web playground
adk web

# Or use the custom professional interface
python -m http.server 8080 --directory web_interface
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Etsy Business Manager                      │
│                 (Orchestrator Agent)                    │
└────────────┬────────────────────────────┬───────────────┘
             │                            │
    ┌────────▼────────┐        ┌──────────▼──────────┐
    │  Inventory      │        │  Marketing         │
    │  Agent          │        │  Agent             │
    │                 │        │  (Instagram)       │
    │ • Stock levels  │        │                    │
    │ • Low-stock     │        │ • Caption gen     │
    │   alerts        │        │ • Hashtag research│
    │ • Cost tracking │        │ • Post scheduling │
    └────────┬────────┘        └──────────┬──────────┘
             │                            │
    ┌────────▼────────┐        ┌──────────▼──────────┐
    │  Client Comm    │        │  Shipping          │
    │  Agent          │        │  Agent             │
    │                 │        │                    │
    │ • Auto-replies  │        │ • Rate calculation │
    │ • Order updates │        │ • Label generation │
    │ • Review mgmt   │        │ • Carrier compare  │
    └────────┬────────┘        └──────────┬──────────┘
             │                            │
             └────────────┬───────────────┘
                          │
                   ┌──────▼──────┐
                   │  Reminder   │
                   │  Agent      │
                   │             │
                   │ • Deadlines │
                   │ • Followups │
                   │ • Restocks  │
                   └─────────────┘
```

---

## 📁 Project Structure

```
etsy-art-agent/
├── etsy_business_manager/      # ADK Agent Project
│   ├── agent.py                  # Main orchestrator
│   ├── config/
│   │   └── settings.py           # Configuration & constants
│   ├── agents/
│   │   ├── inventory_agent.py    # Stock & inventory management
│   │   ├── marketing_agent.py    # Instagram promo & content
│   │   ├── client_comm_agent.py  # Customer communication
│   │   ├── shipping_agent.py     # Shipping & logistics
│   │   └── reminder_agent.py     # Smart reminders & deadlines
│   ├── tools/
│   │   ├── inventory_tools.py    # Inventory CRUD tools
│   │   ├── marketing_tools.py    # Content generation tools
│   │   ├── communication_tools.py# Email/message tools
│   │   ├── shipping_tools.py     # Shipping calculation tools
│   │   └── reminder_tools.py    # Calendar/reminder tools
│   ├── data/                     # Local data storage
│   └── tests/                    # Unit & integration tests
├── web_interface/                # Professional Web UI
│   ├── index.html
│   ├── css/style.css
│   └── js/app.js
├── docs/
│   └── architecture.md
├── requirements.txt
├── setup.sh / setup.bat
└── README.md
```

---

## 🤖 Agent Capabilities

| Agent | Role | Key Features |
|-------|------|-------------|
| **Inventory Agent** | Stock Manager | Track handmade items (keychains, jewelry, crochet, bookmarks), low-stock alerts, material cost tracking, supplier notes |
| **Marketing Agent** | Social Media Manager | Generate Instagram captions, hashtag research, product photography tips, promotional campaign ideas, trend analysis |
| **Client Communication** | Customer Support | Draft professional responses, order status updates, review thank-you messages, custom request handling |
| **Shipping Agent** | Logistics Coordinator | Calculate shipping costs (USPS, UPS, FedEx), packaging recommendations, international customs guidance, label prep |
| **Reminder Agent** | Personal Assistant | Craft fair deadlines, restock reminders, follow-up with wholesale clients, tax filing reminders, supply run alerts |

---

## 🛠️ Tech Stack

- **Framework**: Google ADK (Agent Development Kit) citeweb_search:1#5
- **CLI**: `agents-cli` for scaffolding, eval, and deployment citeweb_search:1#3
- **Models**: Gemini 2.5 Flash (primary), Gemini 2.5 Pro (complex reasoning)
- **Deployment**: Cloud Run / Vertex AI Agent Engine (via `agents-cli deploy`)
- **Frontend**: Vanilla HTML5 + CSS3 + JavaScript (zero-dependency, fast)
- **Storage**: Local JSON (dev) / Firestore (production)

---

## 🧪 Testing & Evaluation

```bash
# Run agent evaluation
agents-cli eval generate
agents-cli eval grade

# Run unit tests
pytest etsy_business_manager/tests/
```

---

## 📦 Deployment

```bash
# Deploy to Google Cloud Run
agents-cli deploy --target cloud_run --project YOUR_PROJECT_ID

# Or deploy to Vertex AI Agent Engine
agents-cli deploy --target agent_runtime --project YOUR_PROJECT_ID

# Register with Gemini Enterprise
agents-cli publish gemini-enterprise
```

---

## 📝 License

MIT License — Built for the Google 5-Day Capstone Project.

---

## 🙌 Acknowledgments

- Google Agent Development Kit (ADK) Team
- Google Agents CLI Team
- Gemini API
