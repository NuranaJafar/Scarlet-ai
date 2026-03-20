from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Conversation, Message
# from app.services.ai_service import AIService
# from app.utils.validators import validate_message

api_bp = Blueprint('api', __name__)
# chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')
# ai_service = AIService()

# Root endpoint
@api_bp.route('/', methods=['GET'])
def root():
    """Root API endpoint"""
    return jsonify({
        'app': 'Scarlet Witch AI',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'health': '/api/health',
            'chat': '/api/chat/send (use routes/chat.py)',
            'conversations': '/api/chat/conversations'
        }
    }), 200

# Health check endpoint
@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Scarlet Witch AI is running'}), 200

# Chat endpoints - DISABLED (duplicates routes/chat.py)
# @chat_bp.route('/send', methods=['POST'])
# @login_required
# def send_message():
#     pass  # See routes/chat.py

# ... other chat routes commented out

# Note: Register api_bp in __init__.py if needed, but chat_bp routes disabled to avoid conflicts
