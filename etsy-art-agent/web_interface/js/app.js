// ArtisanManager JS Controller - Live Web API Connector
document.addEventListener('DOMContentLoaded', () => {
    // Initial fetch from backend APIs
    refreshAllData();

    // Event listeners
    document.getElementById('sendBtn').addEventListener('click', sendChatMessage);
    document.getElementById('chatInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendChatMessage();
    });

    // Alert Bell dropdown toggle
    document.getElementById('alertBell').addEventListener('click', (e) => {
        e.stopPropagation();
        document.getElementById('alertsDropdown').classList.toggle('show');
    });
    
    document.addEventListener('click', () => {
        document.getElementById('alertsDropdown').classList.remove('show');
    });

    document.getElementById('alertsDropdown').addEventListener('click', (e) => {
        e.stopPropagation();
    });
});

// App State Cache
let state = {
    inventory: [],
    clients: [],
    messages: [],
    reminders: [],
    orders: [],
    activeSection: 'dashboard'
};

// Refresh all dashboard assets
function refreshAllData() {
    fetchInventory();
    fetchCustomers();
    fetchReminders();
    fetchOrders();
}

// Navigation Tabs
function switchSection(targetSection) {
    state.activeSection = targetSection;
    
    // Toggle active classes on nav
    document.querySelectorAll('.nav-item').forEach(item => {
        if (item.dataset.section === targetSection) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });

    // Toggle active section views
    document.querySelectorAll('.content-section').forEach(sec => {
        if (sec.id === targetSection) {
            sec.classList.add('active');
        } else {
            sec.classList.remove('active');
        }
    });

    // Specific tab activations
    if (targetSection === 'dashboard') {
        renderCRMPipeline();
    }
}

// ==========================================
// 1. CHAT LOGIC WITH ACTUAL PYTHON BACKEND
// ==========================================
async function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const text = input.value.trim();
    if (!text) return;

    // Render user message bubble
    appendChatBubble(text, 'user');
    input.value = '';

    // Render loading indicator bubble
    const loadingId = appendLoadingBubble();

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: text })
        });
        const data = await response.json();
        
        // Remove loading bubble
        removeBubble(loadingId);

        if (data.error) {
            appendChatBubble(`⚠️ Error: ${data.error}`, 'agent');
        } else {
            // Update connection badge based on API status
            updateConnectionBadge(data.metadata.api_connected);
            
            // Build metadata line for sub-agent tracking
            let metadataStr = `<div class="sub-agent-tag">Delegated: <strong>${data.metadata.delegated_agent}</strong>`;
            if (data.metadata.tools_used && data.metadata.tools_used.length > 0) {
                metadataStr += ` | Tools: <code>${data.metadata.tools_used.join(', ')}</code>`;
            }
            metadataStr += `</div>`;

            appendChatBubble(data.response + metadataStr, 'agent');
            
            // Refresh data after any action that could change database state
            refreshAllData();
        }
    } catch (err) {
        removeBubble(loadingId);
        appendChatBubble("❌ Unable to connect to the backend server. Make sure server.py is running.", "agent");
        console.error("Chat error:", err);
    }
}

function triggerQuickAction(promptText) {
    document.getElementById('chatInput').value = promptText;
    sendChatMessage();
}

function appendChatBubble(htmlContent, sender) {
    const chatContainer = document.getElementById('chatContainer');
    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-message ${sender}`;

    const avatar = sender === 'agent' ? '✧' : '👤';
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    msgDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            <p>${htmlContent}</p>
            <span class="message-time">${time}</span>
        </div>
    `;
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function appendLoadingBubble() {
    const chatContainer = document.getElementById('chatContainer');
    const loadingDiv = document.createElement('div');
    const id = 'loading-' + Math.random().toString(36).substr(2, 9);
    loadingDiv.id = id;
    loadingDiv.className = 'chat-message agent';

    loadingDiv.innerHTML = `
        <div class="message-avatar">✧</div>
        <div class="message-content">
            <p class="loading-dots">Coordinating sub-agents<span>.</span><span>.</span><span>.</span></p>
        </div>
    `;
    chatContainer.appendChild(loadingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    return id;
}

function removeBubble(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

function updateConnectionBadge(connected) {
    const badge = document.getElementById('connectionBadge');
    const text = document.getElementById('connectionText');
    if (connected) {
        badge.className = "status-badge connected";
        text.textContent = "Gemini Live";
    } else {
        badge.className = "status-badge";
        text.textContent = "Offline Mode";
    }
}

// ==========================================
// 2. INVENTORY MANAGEMENT ROUTINES
// ==========================================
async function fetchInventory() {
    try {
        const response = await fetch('/api/inventory');
        const data = await response.json();
        state.inventory = data.items || [];
        renderInventoryTable();
        updateDashboardMetrics();
        syncMarketingDropdown();
        checkLowStockAlerts();
    } catch (err) {
        console.error("Failed to load inventory:", err);
    }
}

function renderInventoryTable() {
    const tbody = document.getElementById('inventoryTableBody');
    tbody.innerHTML = '';

    let totalCapital = 0;
    let totalRevenue = 0;

    state.inventory.forEach(item => {
        const qty = item.quantity;
        const cost = item.material_cost;
        const price = item.selling_price;
        const profit = price - cost;
        const marginPercent = price > 0 ? ((profit / price) * 100).toFixed(0) : 0;
        
        // Sum capital and sales
        totalCapital += cost * qty;
        totalRevenue += price * qty;

        // Stock status categorization
        let statusClass = 'sufficient';
        let statusLabel = 'Stock Ok';
        if (qty <= item.low_stock_threshold) {
            statusClass = 'low';
            statusLabel = 'Low Stock';
        }
        if (qty <= 2) {
            statusClass = 'critical';
            statusLabel = 'Critical';
        }

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>${item.item_id}</strong></td>
            <td>${item.name}</td>
            <td><span class="badge">${item.category}</span></td>
            <td>
                <div class="stock-controls">
                    <span class="stock-tag ${statusClass}">${qty} (${statusLabel})</span>
                    <button class="btn-stock-adjust" onclick="adjustStock('${item.item_id}', 1)">+</button>
                    <button class="btn-stock-adjust" onclick="adjustStock('${item.item_id}', -1)">-</button>
                </div>
            </td>
            <td>$${cost.toFixed(2)}</td>
            <td>$${price.toFixed(2)}</td>
            <td style="color: ${marginPercent >= 70 ? 'var(--success)' : marginPercent >= 50 ? 'var(--warning)' : 'var(--danger)'}">
                $${profit.toFixed(2)} (${marginPercent}%)
            </td>
            <td>
                <button class="btn-table-action" onclick="quickEditItem('${item.item_id}')">Edit</button>
            </td>
        `;
        tbody.appendChild(tr);
    });

    document.getElementById('calcMaterialCapital').textContent = `$${totalCapital.toFixed(2)}`;
    document.getElementById('calcPotentialRevenue').textContent = `$${totalRevenue.toFixed(2)}`;
    document.getElementById('calcPotentialProfit').textContent = `$${(totalRevenue - totalCapital).toFixed(2)}`;
}

async function adjustStock(itemId, val) {
    try {
        const response = await fetch('/api/inventory/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ item_id: itemId, quantity_change: val })
        });
        const data = await response.json();
        fetchInventory(); // Reload table
    } catch (err) {
        console.error("Error updating stock:", err);
    }
}

// Modal handling
function openModal(id) {
    document.getElementById(id).classList.add('open');
}

function closeModal(id) {
    document.getElementById(id).classList.remove('open');
}

async function submitNewProduct() {
    const name = document.getElementById('addProdName').value;
    const category = document.getElementById('addProdCategory').value;
    const qty = parseInt(document.getElementById('addProdQty').value);
    const cost = parseFloat(document.getElementById('addProdCost').value);
    const price = parseFloat(document.getElementById('addProdPrice').value);
    const materials = document.getElementById('addProdMaterials').value.split(',').map(m => m.trim());
    const makeTime = parseInt(document.getElementById('addProdTime').value);
    const tags = document.getElementById('addProdTags').value.split(',').map(t => t.trim());

    if (!name) {
        alert("Please enter a product name.");
        return;
    }

    try {
        const response = await fetch('/api/inventory/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: name, category: category, quantity: qty, material_cost: cost,
                selling_price: price, materials_used: materials, time_to_make_minutes: makeTime, tags: tags
            })
        });
        
        closeModal('addProductModal');
        fetchInventory();
    } catch (err) {
        console.error("Error adding product:", err);
    }
}

function filterInventory() {
    const query = document.getElementById('inventorySearch').value.toLowerCase();
    const filter = document.getElementById('inventoryCategoryFilter').value;
    const rows = document.querySelectorAll('#inventoryTableBody tr');

    rows.forEach(row => {
        const name = row.children[1].textContent.toLowerCase();
        const cat = row.children[2].textContent.toLowerCase();
        const matchesQuery = name.includes(query);
        const matchesFilter = filter === 'all' || cat.includes(filter);

        if (matchesQuery && matchesFilter) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

function quickEditItem(itemId) {
    // Fill chat query to edit item via assistant
    triggerQuickAction(`I want to edit the item details for product ID ${itemId}. Please show details.`);
    switchSection('dashboard');
}

// ==========================================
// 3. INSTAGRAM MARKETING HUB ROUTINES
// ==========================================
function syncMarketingDropdown() {
    const select = document.getElementById('mktProductSelect');
    select.innerHTML = '';
    state.inventory.forEach(item => {
        const opt = document.createElement('option');
        opt.value = item.name;
        opt.dataset.category = item.category;
        opt.textContent = `${item.name} (${item.category})`;
        select.appendChild(opt);
    });
    syncMarketingProductMeta();
}

function syncMarketingProductMeta() {
    const select = document.getElementById('mktProductSelect');
    const selectedOpt = select.options[select.selectedIndex];
    if (selectedOpt) {
        document.getElementById('mktProductType').value = selectedOpt.dataset.category;
    }
}

function applyCampaignTemplate() {
    const template = document.getElementById('mktTemplate').value;
    const mood = document.getElementById('mktMood');

    if (template === 'seasonal_sale') {
        mood.value = 'playful';
    } else if (template === 'behind_the_scenes') {
        mood.value = 'cozy';
    } else if (template === 'flash_sale') {
        mood.value = 'minimalist';
    } else {
        mood.value = 'warm';
    }
}

async function generateMarketingContent() {
    const pname = document.getElementById('mktProductSelect').value;
    const ptype = document.getElementById('mktProductType').value;
    const mood = document.getElementById('mktMood').value;
    
    const outputText = document.getElementById('igCaptionText');
    const igPhotoPlaceholder = document.getElementById('igPhotoPlaceholder');
    
    outputText.textContent = "Writing your campaign copy using the sub-agent...";

    try {
        const response = await fetch('/api/marketing/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_name: pname, product_type: ptype, mood: mood })
        });
        const data = await response.json();
        
        if (data.caption) {
            outputText.textContent = data.caption;
            // Update preview photo placeholder with category aesthetic
            igPhotoPlaceholder.textContent = `${ptype.toUpperCase()} SHOWCASE`;
        } else {
            outputText.textContent = "⚠️ Error generating caption.";
        }
    } catch (err) {
        outputText.textContent = "❌ Failed to query marketing generator API.";
    }
}

// ==========================================
// 4. CLIENT CRM & LOGGING ROUTINES
// ==========================================
async function fetchCustomers() {
    try {
        const response = await fetch('/api/customers');
        const data = await response.json();
        state.clients = data.clients || [];
        state.messages = data.messages || [];

        renderCustomersList();
        renderMessagesInbox();
    } catch (err) {
        console.error("Failed to load customer list:", err);
    }
}

function renderCustomersList() {
    const tbody = document.getElementById('crmCustomerList');
    tbody.innerHTML = '';

    const suggestions = document.getElementById('clientSuggestions');
    suggestions.innerHTML = '';

    state.clients.forEach(c => {
        const tr = document.createElement('tr');
        
        // Tags building
        let tagBadges = c.tags.map(t => `<span class="badge" style="margin-right: 4px;">${t}</span>`).join('');

        tr.innerHTML = `
            <td><strong>${c.name}</strong><br><span style="font-size: 11px; color:var(--text-muted)">${c.note}</span></td>
            <td>${c.email}</td>
            <td>${c.total_orders} Orders</td>
            <td>${tagBadges}</td>
        `;
        tbody.appendChild(tr);

        // Fill datalist suggestions
        const opt = document.createElement('option');
        opt.value = c.name;
        suggestions.appendChild(opt);
    });

    document.getElementById('dashboardClientCount').textContent = state.clients.length;
}

function renderMessagesInbox() {
    const tbody = document.getElementById('crmMessagesInbox');
    tbody.innerHTML = '';

    // Sort by timestamp desc
    const sortedMsgs = [...state.messages].sort((a,b) => new Date(b.timestamp) - new Date(a.timestamp));

    sortedMsgs.forEach(m => {
        const client = state.clients.find(c => c.client_id === m.client_id) || { name: "Unknown" };
        const time = new Date(m.timestamp).toLocaleString();
        
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><span style="font-size: 12px; color:var(--text-muted)">${time}</span></td>
            <td><strong>${client.name}</strong></td>
            <td><span class="badge">${m.channel}</span></td>
            <td><span style="font-style: italic">"${m.content}"</span></td>
        `;
        tbody.appendChild(tr);
    });
}

async function saveCustomerInteraction() {
    const name = document.getElementById('logCustomerName').value;
    const channel = document.getElementById('logChannel').value;
    const content = document.getElementById('logContent').value;

    if (!name || !content) {
        alert("Please enter customer name and message content.");
        return;
    }

    try {
        const response = await fetch('/api/customers/log', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: name, channel: channel, content: content })
        });
        
        // Reset logging input
        document.getElementById('logCustomerName').value = '';
        document.getElementById('logContent').value = '';
        
        fetchCustomers();
    } catch (err) {
        console.error("Error logging client interaction:", err);
    }
}

// ==========================================
// 5. SHIPPING CALCULATOR & LABELS
// ==========================================
function syncServiceOptions() {
    const carrier = document.getElementById('shipCarrier').value;
    const service = document.getElementById('shipService');
    service.innerHTML = '';

    if (carrier === 'USPS') {
        service.add(new Option("First Class Package (Standard)", "First Class"));
        service.add(new Option("Priority Mail Box", "Priority"));
        service.add(new Option("Priority Flat Rate Envelope", "Flat Rate"));
    } else if (carrier === 'UPS') {
        service.add(new Option("UPS Ground Saver", "Ground"));
        service.add(new Option("UPS 3 Day Select", "3 Day Select"));
    } else if (carrier === 'FedEx') {
        service.add(new Option("FedEx Home Delivery", "Ground"));
        service.add(new Option("FedEx Express Saver", "Express"));
    }
}

async function estimateShippingRates() {
    const weight = parseFloat(document.getElementById('shipWeight').value);
    const carrier = document.getElementById('shipCarrier').value;
    const service = document.getElementById('shipService').value;
    const pkg = document.getElementById('shipPackaging').value;
    const dest = document.getElementById('shipDest').value;

    const labelWeight = document.getElementById('labelWeight');
    const labelCost = document.getElementById('labelCost');
    const labelCarrier = document.getElementById('labelCarrier');
    const labelTrackingNum = document.getElementById('labelTrackingNum');
    const recommendBox = document.getElementById('shippingRecommendText');

    try {
        const response = await fetch('/api/shipping/calculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                weight_oz: weight, carrier: carrier, service_type: service,
                destination: dest, package_type: pkg
            })
        });
        const data = await response.json();

        // Parse cost from rate string output if possible
        // Example output: "USPS First Class Parcel Rate: $5.50..."
        let costMatch = data.rate.match(/\$[0-9]+\.[0-9]{2}/);
        let costStr = costMatch ? costMatch[0] : "$5.50";

        // Update Label
        labelWeight.textContent = `${weight} oz`;
        labelCost.textContent = costStr;
        labelCarrier.textContent = `${carrier} ${service.toUpperCase()}`;
        
        // Random tracking generator
        labelTrackingNum.textContent = `${carrier.substring(0,2).toUpperCase()}-${Math.floor(10000000000000 + Math.random() * 90000000000000)}`;

        // Display recommendation text
        recommendBox.innerHTML = `<strong>Logistics sub-agent Advice:</strong> ${data.recommendation}`;
    } catch (err) {
        console.error("Rates fetch issue:", err);
    }
}

// ==========================================
// 6. REMINDERS & TASK BOARD
// ==========================================
async function fetchReminders() {
    try {
        const response = await fetch('/api/reminders');
        const data = await response.json();
        state.reminders = data.reminders || [];
        renderRemindersList();
    } catch (err) {
        console.error("Failed to load reminders board:", err);
    }
}

function renderRemindersList(filterCategory = 'all') {
    const list = document.getElementById('remindersListContainer');
    list.innerHTML = '';

    let pendingCount = 0;

    state.reminders.forEach(rem => {
        const isCompleted = rem.status === 'completed';
        if (!isCompleted) pendingCount++;

        // Filter verification
        if (filterCategory !== 'all' && rem.category !== filterCategory) return;

        const li = document.createElement('li');
        li.className = `reminder-item ${isCompleted ? 'completed' : ''}`;
        
        const catClass = rem.category.toLowerCase().replace(' ', '');

        li.innerHTML = `
            <input type="checkbox" class="reminder-checkbox" ${isCompleted ? 'checked' : ''} onchange="toggleReminder('${rem.reminder_id}')">
            <div class="reminder-info">
                <div class="reminder-title">${rem.title}</div>
                <div class="reminder-meta">
                    <span class="reminder-category ${catClass}">${rem.category}</span>
                    <span class="reminder-due">📅 Due: ${rem.due_date}</span>
                    <span style="font-size:11px; color:var(--text-muted)">| ${rem.notes}</span>
                </div>
            </div>
        `;
        list.appendChild(li);
    });

    document.getElementById('dashboardPendingTasks').textContent = pendingCount;
}

function filterReminders(category) {
    // Manage active tag headers
    const filters = document.querySelectorAll('.category-filters .filter-tag');
    filters.forEach(f => {
        if (f.textContent.includes(category) || (category === 'all' && f.textContent === 'All')) {
            f.classList.add('active');
        } else {
            f.classList.remove('active');
        }
    });

    renderRemindersList(category);
}

async function addNewReminder() {
    const title = document.getElementById('remTitle').value;
    const cat = document.getElementById('remCategory').value;
    const date = document.getElementById('remDueDate').value;
    const notes = document.getElementById('remNotes').value;

    if (!title || !date) {
        alert("Please specify a reminder title and completion date.");
        return;
    }

    try {
        const response = await fetch('/api/reminders/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: title, category: cat, due_date: date, notes: notes })
        });
        
        // Reset fields
        document.getElementById('remTitle').value = '';
        document.getElementById('remDueDate').value = '';
        document.getElementById('remNotes').value = '';
        
        fetchReminders();
    } catch (err) {
        console.error("Failed to append reminder:", err);
    }
}

async function toggleReminder(reminderId) {
    try {
        const response = await fetch('/api/reminders/toggle', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ reminder_id: reminderId })
        });
        fetchReminders();
    } catch (err) {
        console.error("Failed toggle reminder status:", err);
    }
}

// ==========================================
// 7. MOCK CRM PIPELINE DRAG & STATUS
// ==========================================
async function fetchOrders() {
    try {
        const response = await fetch('/api/orders');
        const data = await response.json();
        state.orders = data.orders || [];
        renderCRMPipeline();
    } catch (err) {
        console.error("Failed loading order pipeline:", err);
    }
}

function renderCRMPipeline() {
    const columns = {
        'Inquiry': document.getElementById('crmInquiry'),
        'Sketching': document.getElementById('crmSketching'),
        'In Production': document.getElementById('crmProduction'),
        'Shipped': document.getElementById('crmShipped')
    };

    // Clean containers
    Object.keys(columns).forEach(key => { if (columns[key]) columns[key].innerHTML = ''; });

    state.orders.forEach(ord => {
        const col = columns[ord.status];
        if (!col) return;

        const card = document.createElement('div');
        card.className = 'crm-card';
        
        // Check items listing
        let itemsStr = ord.items.map(i => `${i.quantity}x ${i.name}`).join(', ');
        let totalValue = ord.items.reduce((acc, i) => acc + (i.price * i.quantity), 0);

        // Progress button based on status
        let progressBtn = '';
        if (ord.status === 'Inquiry') {
            progressBtn = `<button class="btn-crm-action" onclick="updateOrderStatus('${ord.order_id}', 'Sketching')">Sketch ➜</button>`;
        } else if (ord.status === 'Sketching') {
            progressBtn = `<button class="btn-crm-action" onclick="updateOrderStatus('${ord.order_id}', 'In Production')">Produce ➜</button>`;
        } else if (ord.status === 'In Production') {
            progressBtn = `<button class="btn-crm-action" onclick="updateOrderStatus('${ord.order_id}', 'Shipped')">Ship ➜</button>`;
        } else {
            progressBtn = `<span style="color:var(--success)">📦 Completed</span>`;
        }

        card.innerHTML = `
            <div class="crm-card-title">${itemsStr}</div>
            <div class="crm-card-customer">Client: ${ord.client_name}</div>
            <div class="crm-card-meta">
                <span class="crm-card-price">$${totalValue.toFixed(2)}</span>
                ${progressBtn}
            </div>
        `;
        col.appendChild(card);
    });
}

async function updateOrderStatus(orderId, newStatus) {
    try {
        const response = await fetch('/api/orders/update_status', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ order_id: orderId, status: newStatus })
        });
        fetchOrders();
    } catch (err) {
        console.error("Failed to update status:", err);
    }
}

// ==========================================
// 8. CRITICAL SHOP ALERTS BELL & METRICS
// ==========================================
function updateDashboardMetrics() {
    // Calculate total inventory value
    let totalVal = 0;
    state.inventory.forEach(item => {
        totalVal += item.selling_price * item.quantity;
    });
    
    document.getElementById('dashboardStockValue').textContent = `$${totalVal.toFixed(2)}`;
    document.getElementById('dashboardActiveItems').textContent = `${state.inventory.length} Products Loaded`;
}

function checkLowStockAlerts() {
    const list = document.getElementById('alertList');
    const bell = document.getElementById('alertBell');
    const cardText = document.getElementById('dashboardLowStockCount');
    const lowStockCard = document.getElementById('lowStockCard');

    list.innerHTML = '';
    let criticalItems = [];
    let warningItems = [];

    state.inventory.forEach(item => {
        if (item.quantity <= 2) {
            criticalItems.push(item);
        } else if (item.quantity <= item.low_stock_threshold) {
            warningItems.push(item);
        }
    });

    const totalAlertsCount = criticalItems.length + warningItems.length;
    cardText.textContent = totalAlertsCount;

    if (totalAlertsCount > 0) {
        bell.classList.add('alert-active');
        if (criticalItems.length > 0) {
            lowStockCard.className = "metric-card alert critical";
        } else {
            lowStockCard.className = "metric-card alert";
        }
    } else {
        bell.classList.remove('alert-active');
        lowStockCard.className = "metric-card";
    }

    if (totalAlertsCount === 0) {
        list.innerHTML = '<li>✅ All supplies are well-stocked!</li>';
        return;
    }

    criticalItems.forEach(item => {
        const li = document.createElement('li');
        li.className = 'danger';
        li.innerHTML = `🚨 <strong>CRITICAL STOCK:</strong> ${item.name} has only <strong>${item.quantity} left!</strong>`;
        list.appendChild(li);
    });

    warningItems.forEach(item => {
        const li = document.createElement('li');
        li.className = 'warning';
        li.innerHTML = `⚠️ <strong>LOW STOCK:</strong> ${item.name} has only <strong>${item.quantity} left.</strong>`;
        list.appendChild(li);
    });
}
