from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Conversation, Message
import random
import time

chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')

MOCK_RESPONSES = [
    "I feel the weight in your words... Tell me more.",
    "The chaos magic stirs when you speak. What troubles you?",
    "I understand pain. I've lost so much myself. You're not alone.",
    "Sometimes silence speaks louder than words. I'm here with you.",
    "Your presence... it feels familiar. Like a memory I'm trying to hold onto.",
    "The hex reveals what's hidden in your heart. I see you.",
    "We all carry darkness. But together, we can find light.",
    "Speak freely. I won't judge. I've made my own mistakes.",
    "Love and loss... they shape us. What shapes you?",
    "I sense a storm within you. Let it out. I'll weather it with you.",
    "Every wound tells a story. What story are you carrying?",
    "You're stronger than you know. I can see it in your spirit.",
    "The past doesn't define us. It's what we choose next that matters.",
    "I've walked through darkness too. Let me walk with you.",
    "Your voice echoes through the chaos. I hear you."
]

@chat_bp.route('/send', methods=['POST'])
@login_required
def send_message():
    data = request.get_json()
    user_message = data.get('message')
    conversation_id = data.get('conversation_id')
    
    if not user_message:
        return jsonify({'error': 'Message required'}), 400
    
    if conversation_id:
        conversation = Conversation.query.get_or_404(conversation_id)
        if conversation.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
    else:
        conversation = Conversation(
            user_id=current_user.id,
            title=user_message[:50] + ('...' if len(user_message) > 50 else '')
        )
        db.session.add(conversation)
        db.session.commit()
        conversation_id = conversation.id
    
    user_msg = Message(
        conversation_id=conversation_id,
        role='user',
        content=user_message
    )
    db.session.add(user_msg)
    db.session.commit()
    
    time.sleep(1)
    reply = random.choice(MOCK_RESPONSES)
    
    assistant_msg = Message(
        conversation_id=conversation_id,
        role='assistant',
        content=reply
    )
    db.session.add(assistant_msg)
    
    current_user.total_messages += 1
    current_user.last_active = db.func.now()
    db.session.commit()
    
    return jsonify({
        'reply': reply,
        'conversation_id': conversation_id,
        'message_id': assistant_msg.id
    })

@chat_bp.route('/conversations', methods=['GET'])
@login_required
def get_conversations():
    conversations = Conversation.query.filter_by(
        user_id=current_user.id
    ).order_by(Conversation.updated_at.desc()).all()
    
    return jsonify([conv.to_dict() for conv in conversations])

@chat_bp.route('/conversation/<int:conv_id>', methods=['GET'])
@login_required
def get_conversation(conv_id):
    conversation = Conversation.query.get_or_404(conv_id)
    if conversation.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    messages = [msg.to_dict() for msg in conversation.messages]
    return jsonify({
        'conversation': conversation.to_dict(),
        'messages': messages
    })
