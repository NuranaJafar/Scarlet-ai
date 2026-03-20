def validate_message(data):
    """Validate message data"""
    if not isinstance(data, dict):
        return False
    
    if 'message' not in data or not isinstance(data['message'], str):
        return False
    
    if not data['message'].strip():
        return False
    
    return True

def validate_email(email):
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_username(username):
    """Validate username"""
    if not isinstance(username, str):
        return False
    
    if len(username) < 3 or len(username) > 80:
        return False
    
    if not username.replace('_', '').replace('-', '').isalnum():
        return False
    
    return True

def validate_password(password):
    """Validate password strength"""
    if not isinstance(password, str):
        return False
    
    if len(password) < 8:
        return False
    
    return True
