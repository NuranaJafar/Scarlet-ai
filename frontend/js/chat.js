// Chat functionality
class ChatManager {
    constructor() {
        this.app = null;
        this.messagesContainer = document.getElementById('messagesContainer');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.isWaiting = false;
        this.setupEventListeners();
    }
    
    init(app) {
        this.app = app;
    }
    
    setupEventListeners() {
        this.sendBtn?.addEventListener('click', () => this.sendMessage());
        this.messageInput?.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        this.messageInput?.addEventListener('input', () => this.autoResize());
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isWaiting || !this.app?.token) return;
        
        this.isWaiting = true;
        this.addMessage('user', message);
        this.messageInput.value = '';
        this.autoResize();
        this.showTypingIndicator();
        
        try {
            const response = await fetch('/api/chat/send', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.app.token}`
                },
                body: JSON.stringify({
                    message: message,
                    conversation_id: this.app.currentConversation?.id
                })
            });
            
            const data = await response.json();
            this.hideTypingIndicator();
            
            if (response.ok) {
                this.addMessage('assistant', data.reply);
                if (!this.app.currentConversation) {
                    this.app.currentConversation = { id: data.conversation_id };
                    this.app.loadConversations();
                }
            } else {
                this.addMessage('assistant', 'The chaos magic flickers... something went wrong. Try again?');
            }
        } catch (error) {
            this.hideTypingIndicator();
            this.addMessage('assistant', 'The connection to the hex is unstable. Please make sure the server is running.');
        } finally {
            this.isWaiting = false;
            this.messageInput.focus();
        }
    }
    
    addMessage(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas ${role === 'user' ? 'fa-user' : 'fa-crown'}"></i>
            </div>
            <div class="message-bubble">
                ${this.escapeHtml(content)}
                <div class="message-timestamp">${timestamp}</div>
            </div>
        `;
        
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    loadMessages(messages) {
        this.clearMessages();
        messages.forEach(msg => {
            this.addMessage(msg.role, msg.content);
        });
    }
    
    clearMessages() {
        this.messagesContainer.innerHTML = '';
    }
    
    showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'message wanda';
        indicator.id = 'typingIndicator';
        indicator.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-crown"></i>
            </div>
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;
        this.messagesContainer.appendChild(indicator);
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) indicator.remove();
    }
    
    autoResize() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(110, this.messageInput.scrollHeight) + 'px';
    }
    
    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
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
}

// Initialize chat manager
window.chat = new ChatManager();