// Etsy Business Manager - Web Interface Controller

const sections = document.querySelectorAll('.content-section');
const navItems = document.querySelectorAll('.nav-item');
const chatContainer = document.getElementById('chatContainer');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');

// Navigation
navItems.forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        const target = item.dataset.section;

        navItems.forEach(n => n.classList.remove('active'));
        item.classList.add('active');

        sections.forEach(s => s.classList.remove('active'));
        document.getElementById(target).classList.add('active');
    });
});

// Chat functionality
function addMessage(text, sender = 'user') {
    const div = document.createElement('div');
    div.className = `chat-message ${sender}`;

    const avatar = sender === 'agent' 
        ? '<div class="message-avatar">🎨</div>' 
        : '<div class="message-avatar" style="background:#e2e8f0;">👤</div>';

    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    div.innerHTML = `
        ${avatar}
        <div class="message-content">
            <p>${text}</p>
            <span class="message-time">${time}</span>
        </div>
    `;

    chatContainer.appendChild(div);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function sendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    addMessage(text, 'user');
    chatInput.value = '';

    setTimeout(() => {
        const response = generateAgentResponse(text);
        addMessage(response, 'agent');
    }, 800);
}

sendBtn.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

function generateAgentResponse(input) {
    const lower = input.toLowerCase();

    if (lower.includes('inventory') || lower.includes('stock') || lower.includes('how many')) {
        return "I'll check your inventory right away! You currently have 12 active products across keychains, jewelry, crochet, and bookmarks. Would you like me to show low-stock items or add a new product?";
    }
    if (lower.includes('instagram') || lower.includes('caption') || lower.includes('post')) {
        return "I can help you create Instagram content! I can generate captions, research hashtags, or plan your content calendar. What product would you like to feature?";
    }
    if (lower.includes('shipping') || lower.includes('cost') || lower.includes('usps')) {
        return "I can calculate shipping costs across USPS, UPS, and FedEx. What's the total weight of the package and where is it going?";
    }
    if (lower.includes('customer') || lower.includes('email') || lower.includes('reply')) {
        return "I'll help you draft a professional customer response. What's the customer's name and what are they asking about?";
    }
    if (lower.includes('reminder') || lower.includes('deadline') || lower.includes('craft fair')) {
        return "I can set reminders for craft fairs, tax deadlines, restocking, or follow-ups. What would you like to be reminded about and when?";
    }

    return "I'm here to help manage your handmade business! I can assist with inventory tracking, Instagram marketing, customer communications, shipping calculations, and setting reminders. What would you like to work on?";
}

// Quick Actions
function quickAction(action) {
    const messages = {
        'check_stock': 'Check my current inventory',
        'low_stock': 'Show me low stock alerts',
        'create_caption': 'Write an Instagram caption for my best-selling item',
        'shipping_cost': 'Calculate shipping for a 2oz package to California',
        'draft_reply': 'Help me draft a reply to a customer asking about custom orders',
        'set_reminder': 'Set a reminder for the craft fair application deadline'
    };

    chatInput.value = messages[action];
    sendMessage();
}

// Caption Generator
function generateCaption() {
    const product = document.getElementById('capProduct').value || 'Handmade Item';
    const type = document.getElementById('capType').value;
    const mood = document.getElementById('capMood').value;

    const captions = {
        'warm': `There's something so special about handmade ${type}s... 💕\n\nIntroducing the ${product}! Each piece is carefully crafted by hand, making every item truly one-of-a-kind. 🎨\n\nWhether you're treating yourself or looking for the perfect gift, this ${type} brings a personal touch that mass-produced items simply can't match. 💝\n\n✨ Link in bio to shop! ✨\n\n#handmade #etsyshop #smallbusiness #handcrafted #shopsmall #makersgonnamake #supportsmallbusiness`,
        'playful': `Obsessed with this ${product}! 🎉\n\nYour new favorite ${type} just dropped! 🚀 Who says handmade can't be fun? 🌈\n\nThe ${product} is here to add some joy to your day. Handcrafted with love and a sprinkle of creativity! ✨\n\n🛍️ Tap the link in our bio to make it yours!\n\n#handmade #etsyshop #smallbusiness #handcrafted #shopsmall #makersgonnamake`,
        'elegant': `Timeless beauty in every detail. 🕊️\n\nThe ${product} — crafted for those who appreciate the finer things. 💎\n\nElegance, handmade. Each ${type} is a small work of art, designed to be cherished. ✨\n\n✨ Link in bio to shop! ✨\n\n#handmade #etsyshop #smallbusiness #artisan #handcrafted #elegant #shopsmall`
    };

    document.getElementById('captionOutput').textContent = captions[mood] || captions['warm'];
}

// Load demo data
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('inventoryCount').textContent = '12';
    document.getElementById('lowStockCount').textContent = '3';
    document.getElementById('upcomingTasks').textContent = '5';
    document.getElementById('scheduledPosts').textContent = '2';
});
