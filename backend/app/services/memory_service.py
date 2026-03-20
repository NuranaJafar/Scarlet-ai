import redis
import os
import json
from datetime import datetime, timedelta

class MemoryService:
    def __init__(self):
        self.redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))
    
    def store_memory(self, user_id, key, value, ttl_days=30):
        data = {
            'value': value,
            'created_at': datetime.utcnow().isoformat(),
            'ttl': ttl_days
        }
        self.redis_client.setex(f'memory:{user_id}:{key}', timedelta(days=ttl_days), json.dumps(data))
    
    def get_memory(self, user_id, key):
        data = self.redis_client.get(f'memory:{user_id}:{key}')
        return json.loads(data) if data else None
    
    def get_all_memories(self, user_id):
        keys = self.redis_client.keys(f'memory:{user_id}:*')
        memories = []
        for key in keys:
            data = self.redis_client.get(key)
            if data:
                mem = json.loads(data)
                mem['key'] = key.decode().split(':')[-1]
                memories.append(mem)
        return memories

