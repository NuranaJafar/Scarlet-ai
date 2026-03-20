// Main Application Logic
class ScarletWitchApp {
    constructor() {
        this.token = localStorage.getItem('token');
        this.currentUser = null;
        this.currentConversation = null;
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        if (this.token) {
            this.verifyToken();
        } else {
            this.showAuthModal();
        }
    }
    
    setupEventListeners() {
        // Auth tabs
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.switchAuthTab(e.target.dataset.tab));
        });
        
        // Login form
        document.getElementById('loginForm')?.addEventListener('submit', (e) => this.login(e));
        document.getElementById('registerForm')?.addEventListener('submit', (e) => this.register(e));
        
        // Logout
        document.getElementById('logoutBtn')?.addEventListener('click', () => this.logout());
        
        // New chat
        document.getElementById('newChatBtn')?.addEventListener('click', () => this.newConversation());
    }
    
    showAuthModal() {
        document.getElementById('authModal').style.display = 'flex';
    }
    
    hideAuthModal() {
        document.getElementById('authModal').style.display = 'none';
        document.getElementById('chatInterface').style.display = 'flex';
    }
    
    switchAuthTab(tab) {
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelector(`[data-tab="${tab}"]`).classList.add('active');
        
        document.querySelectorAll('.auth-form').forEach(form => form.classList.remove('active'));
        document.getElementById(`${tab}Form`).classList.add('active');
    }
    
    async login(e) {
        e.preventDefault();
        const form = e.target;
        const email = form.querySelector('input[type="email"]').value;
        const password = form.querySelector('input[type="password"]').value;
        
        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
            
            const data = await response.json();
            if (response.ok) {
                this.token = data.token;
                localStorage.setItem('token', this.token);
                this.currentUser = data.user;
                this.hideAuthModal();
                this.loadConversations();
                window.chat.init(this);
            } else {
                this.showError(data.error);
            }
        } catch (error) {
            this.showError('Connection error. Make sure the server is running.');
        }
    }
    
    async register(e) {
        e.preventDefault();
        const form = e.target;
        const username = form.querySelector('input[type="text"]').value;
        const email = form.querySelector('input[type="email"]').value;
        const password = form.querySelector('input[type="password"]').value;
        
        try {
            const response = await fetch('/api/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password })
            });
            
            const data = await response.json();
            if (response.ok) {
                this.token = data.token;
                localStorage.setItem('token', this.token);
                this.currentUser = data.user;
                this.hideAuthModal();
                this.loadConversations();
                window.chat.init(this);
            } else {
                this.showError(data.error);
            }
        } catch (error) {
            this.showError('Connection error. Make sure the server is running.');
        }
    }
    
    async verifyToken() {
        try {
            const response = await fetch('/api/auth/verify', {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.currentUser = data.user;
                this.hideAuthModal();
                this.loadConversations();
                window.chat.init(this);
            } else {
                this.logout();
            }
        } catch (error) {
            this.logout();
        }
    }
    
    logout() {
        localStorage.removeItem('token');
        this.token = null;
        this.currentUser = null;
        document.getElementById('chatInterface').style.display = 'none';
        this.showAuthModal();
    }
    
    async loadConversations() {
        try {
            const response = await fetch('/api/chat/conversations', {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            
            if (response.ok) {
                const conversations = await response.json();
                this.renderConversations(conversations);
            }
        } catch (error) {
            console.error('Failed to load conversations:', error);
        }
    }
    
    renderConversations(conversations) {
        const container = document.getElementById('conversationsList');
        container.innerHTML = conversations.map(conv => `
            <div class="conversation-item ${this.currentConversation?.id === conv.id ? 'active' : ''}" 
                 data-id="${conv.id}">
                <div class="conversation-title">${this.escapeHtml(conv.title)}</div>
                <div class="conversation-date">${new Date(conv.updated_at).toLocaleDateString()}</div>
            </div>
        `).join('');
        
        // Add click handlers
        container.querySelectorAll('.conversation-item').forEach(item => {
            item.addEventListener('click', () => this.loadConversation(item.dataset.id));
        });
    }
    
    async loadConversation(id) {
        try {
            const response = await fetch(`/api/chat/conversation/${id}`, {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.currentConversation = data.conversation;
                window.chat.loadMessages(data.messages);
                this.loadConversations(); // Refresh active state
            }
        } catch (error) {
            console.error('Failed to load conversation:', error);
        }
    }
    
    async newConversation() {
        this.currentConversation = null;
        window.chat.clearMessages();
        this.loadConversations();
    }
    
    escapeHtml(str) {
        if (!str) return '';
        return str.replace(/[&<>]/g, function(m) {
            if (m === '&') return '&amp;';
            if (m === '<') return '&lt;';
            if (m === '>') return '&gt;';
            return m;
        });
    }
    
    showError(message) {
        // Implement toast notification
        alert(message);
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new ScarletWitchApp();
});