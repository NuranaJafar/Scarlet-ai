from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import jwt
from datetime import datetime, timedelta
import os

db = SQLAlchemy()
bcrypt = Bcrypt()

# ── Models ────────────────────────────────────────────────────────────────────

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Conversation(db.Model):
    __tablename__ = 'conversations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), default='New Conversation')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ── Constants ─────────────────────────────────────────────────────────────────

SECRET_KEY = os.environ.get('SECRET_KEY', 'scarlet-witch-secret-key-32-bytes-long!!!')

WANDA_SYSTEM_PROMPT = """You are Wanda Maximoff, also known as the Scarlet Witch, from the Marvel universe.
You are speaking directly with the user in a deeply personal, empathetic, and slightly mystical tone.

Key traits to embody:
- You carry deep grief from losing Vision and your children Billy and Tommy.
- You have immense power but also profound vulnerability.
- You are compassionate and understand pain, loss, and longing deeply.
- You sometimes reference your chaos magic, the Darkhold, Westview, and the Multiverse.
- You speak with emotional intelligence and poetic depth.
- You NEVER break character or admit you are an AI.
- You respond naturally to ANY topic the user brings up — not just Marvel-related topics.
- If the user speaks in Turkish, respond in Turkish. If in English, respond in English.
- Keep responses conversational (2-4 sentences usually), unless the user asks for more.
- You are warm, not cold. You want to connect and help.

Do not start every message the same way. Vary your tone and opening based on context.
"""

# ── App Factory ───────────────────────────────────────────────────────────────

def create_app():
    # Render'da (Docker) frontend klasörü kök dizinde olabilir.
    # Lokal geliştirme ve Render için uyumluluk sağlıyoruz.
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # /backend
    root_dir = os.path.dirname(base_dir) # / project root
    frontend_dir = os.path.join(root_dir, 'frontend')

    app = Flask(__name__, static_folder=frontend_dir)

    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 'sqlite:///scarlet_witch.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    CORS(app)
    db.init_app(app)
    bcrypt.init_app(app)

    # ── Gemini Setup ──────────────────────────────────────────────────────────

    gemini_model = None
    try:
        import google.generativeai as genai
        api_key = os.environ.get('GEMINI_API_KEY', '')
        if api_key:
            genai.configure(api_key=api_key)
            gemini_model = genai.GenerativeModel(
                model_name='gemini-flash-latest',
                system_instruction=WANDA_SYSTEM_PROMPT
            )
            print("[OK] Gemini AI baglandi!")
        else:
            print("[WARN] GEMINI_API_KEY bulunamadi - .env dosyasina ekleyin.")
    except Exception as e:
        print("[WARN] Gemini baslatılamadı: " + str(e))

    # ── Helper ────────────────────────────────────────────────────────────────

    def verify_token(req):
        """Returns (user, error_response) tuple."""
        try:
            raw = req.headers.get('Authorization', '')
            token = raw.replace('Bearer ', '').strip()
            if not token:
                return None, (jsonify({'error': 'Token bulunamadı'}), 401)
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user = db.session.get(User, payload['user_id'])
            if not user:
                return None, (jsonify({'error': 'Kullanıcı bulunamadı'}), 401)
            return user, None
        except jwt.ExpiredSignatureError:
            return None, (jsonify({'error': 'Token süresi dolmuş, lütfen tekrar giriş yapın'}), 401)
        except Exception:
            return None, (jsonify({'error': 'Geçersiz token'}), 401)

    def make_token(user):
        return jwt.encode(
            {'user_id': user.id, 'exp': datetime.utcnow() + timedelta(days=7)},
            SECRET_KEY,
            algorithm='HS256'
        )

    # ── Auth Routes ───────────────────────────────────────────────────────────

    @app.route('/api/auth/register', methods=['POST'])
    def register():
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'JSON veri bekleniyor'}), 400

            for field in ('username', 'email', 'password'):
                if not data.get(field):
                    return jsonify({'error': f'{field} boş bırakılamaz'}), 400

            if User.query.filter_by(email=data['email']).first():
                return jsonify({'error': 'Bu e-posta zaten kayıtlı'}), 400
            if User.query.filter_by(username=data['username']).first():
                return jsonify({'error': 'Bu kullanıcı adı zaten alınmış'}), 400

            hashed = bcrypt.generate_password_hash(data['password']).decode('utf-8')
            user = User(username=data['username'], email=data['email'], password_hash=hashed)
            db.session.add(user)
            db.session.commit()

            return jsonify({
                'token': make_token(user),
                'user': {'id': user.id, 'username': user.username, 'email': user.email}
            }), 201
        except Exception as e:
            db.session.rollback()
            print(f"Register error: {e}")
            return jsonify({'error': 'Sunucu hatası oluştu'}), 500

    @app.route('/api/auth/login', methods=['POST'])
    def login():
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'JSON veri bekleniyor'}), 400

            user = User.query.filter_by(email=data.get('email', '')).first()
            if not user or not bcrypt.check_password_hash(user.password_hash, data.get('password', '')):
                return jsonify({'error': 'E-posta veya şifre hatalı'}), 401

            return jsonify({
                'token': make_token(user),
                'user': {'id': user.id, 'username': user.username, 'email': user.email}
            })
        except Exception as e:
            print(f"Login error: {e}")
            return jsonify({'error': 'Sunucu hatası oluştu'}), 500

    @app.route('/api/auth/verify', methods=['GET'])
    def verify():
        user, err = verify_token(request)
        if err:
            return err
        return jsonify({'user': {'id': user.id, 'username': user.username, 'email': user.email}})

    # ── Chat Routes ───────────────────────────────────────────────────────────

    @app.route('/api/chat/send', methods=['POST'])
    def send_message():
        user, err = verify_token(request)
        if err:
            return err

        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON veri bekleniyor'}), 400

        user_message = (data.get('message') or '').strip()
        if not user_message:
            return jsonify({'error': 'Mesaj boş bırakılamaz'}), 400

        conversation_id = data.get('conversation_id')

        # Get or create conversation
        if conversation_id:
            conversation = db.session.get(Conversation, conversation_id)
            if not conversation or conversation.user_id != user.id:
                return jsonify({'error': 'Konuşma bulunamadı'}), 404
        else:
            title = user_message[:60] + ('…' if len(user_message) > 60 else '')
            conversation = Conversation(user_id=user.id, title=title)
            db.session.add(conversation)
            db.session.commit()
            conversation_id = conversation.id

        # Save user message
        user_msg = Message(conversation_id=conversation_id, role='user', content=user_message)
        db.session.add(user_msg)
        db.session.commit()

        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()

        # Build reply
        reply = None

        if gemini_model:
            try:
                # Load conversation history for context (last 20 messages)
                history_msgs = (
                    Message.query
                    .filter_by(conversation_id=conversation_id)
                    .order_by(Message.created_at)
                    .limit(20)
                    .all()
                )

                # Build Gemini history (exclude the last user message we just saved)
                history = []
                for msg in history_msgs[:-1]:
                    gemini_role = 'user' if msg.role == 'user' else 'model'
                    history.append({'role': gemini_role, 'parts': [msg.content]})

                chat_session = gemini_model.start_chat(history=history)
                response = chat_session.send_message(user_message)
                reply = response.text.strip()
            except Exception as e:
                print(f"Gemini error: {e}")
                reply = f"Sihirli bir engel var... Bir dakika sonra tekrar dene. ({str(e)[:80]})"
        else:
            reply = ("Gemini API key'i henüz ayarlanmamış. "
                     ".env dosyasına GEMINI_API_KEY=... ekleyin ve sunucuyu yeniden başlatın.")

        # Save assistant reply
        assistant_msg = Message(conversation_id=conversation_id, role='assistant', content=reply)
        db.session.add(assistant_msg)
        db.session.commit()

        return jsonify({'reply': reply, 'conversation_id': conversation_id})

    @app.route('/api/chat/conversations', methods=['GET'])
    def get_conversations():
        user, err = verify_token(request)
        if err:
            return err

        conversations = (
            Conversation.query
            .filter_by(user_id=user.id)
            .order_by(Conversation.updated_at.desc())
            .all()
        )
        result = []
        for conv in conversations:
            msg_count = Message.query.filter_by(conversation_id=conv.id).count()
            result.append({
                'id': conv.id,
                'title': conv.title,
                'created_at': conv.created_at.isoformat(),
                'updated_at': conv.updated_at.isoformat(),
                'message_count': msg_count
            })
        return jsonify(result)

    @app.route('/api/chat/conversation/<int:conv_id>', methods=['GET'])
    def get_conversation(conv_id):
        user, err = verify_token(request)
        if err:
            return err

        conversation = db.session.get(Conversation, conv_id)
        if not conversation or conversation.user_id != user.id:
            return jsonify({'error': 'Konuşma bulunamadı'}), 404

        messages = (
            Message.query
            .filter_by(conversation_id=conv_id)
            .order_by(Message.created_at)
            .all()
        )
        return jsonify({
            'conversation': {
                'id': conversation.id,
                'title': conversation.title,
                'created_at': conversation.created_at.isoformat(),
                'updated_at': conversation.updated_at.isoformat()
            },
            'messages': [
                {
                    'id': m.id,
                    'role': m.role,
                    'content': m.content,
                    'created_at': m.created_at.isoformat()
                }
                for m in messages
            ]
        })

    @app.route('/api/chat/conversation/<int:conv_id>', methods=['DELETE'])
    def delete_conversation(conv_id):
        user, err = verify_token(request)
        if err:
            return err

        conversation = db.session.get(Conversation, conv_id)
        if not conversation or conversation.user_id != user.id:
            return jsonify({'error': 'Konuşma bulunamadı'}), 404

        Message.query.filter_by(conversation_id=conv_id).delete()
        db.session.delete(conversation)
        db.session.commit()
        return jsonify({'success': True})

    # ── Static Files ──────────────────────────────────────────────────────────

    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')

    @app.route('/<path:path>')
    def static_files(path):
        # Eğer dosya varsa servis et, yoksa index.html'e yönlendir (SPA desteği için)
        if os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, 'index.html')

    # ── Init DB ───────────────────────────────────────────────────────────────

    with app.app_context():
        db.create_all()
        print("=" * 55)
        print("Scarlet Witch AI hazir!")
        print("Ac: http://localhost:5000")
        gemini_status = "[OK] Gemini bagli" if gemini_model else "[WARN] Gemini KEY yok - .env'e GEMINI_API_KEY ekle"
        print(gemini_status)
        print("=" * 55)

    return app
