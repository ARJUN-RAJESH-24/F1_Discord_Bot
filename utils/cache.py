# Simple cache utility for API responses

import json
import os
from datetime import datetime, timedelta
from typing import Optional, Any
import hashlib

CACHE_DIR = "cache/api_cache"

class SimpleCache:
    """Simple file-based cache for API responses"""
    
    def __init__(self, cache_dir: str = CACHE_DIR):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_path(self, key: str) -> str:
        """Generate cache file path from key"""
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{key_hash}.json")
    
    def get(self, key: str, ttl_seconds: int = 3600) -> Optional[Any]:
        """
        Get value from cache if not expired
        
        Args:
            key: Cache key
            ttl_seconds: Time to live in seconds
        
        Returns:
            Cached value or None if expired/not found
        """
        cache_path = self._get_cache_path(key)
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Check expiration
            cached_time = datetime.fromisoformat(cache_data['timestamp'])
            if datetime.now() - cached_time > timedelta(seconds=ttl_seconds):
                # Expired, delete cache file
                os.remove(cache_path)
                return None
            
            return cache_data['value']
        
        except Exception as e:
            # If any error, delete cache and return None
            try:
                os.remove(cache_path)
            except:
                pass
            return None
    
    def set(self, key: str, value: Any) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
        
        Returns:
            True if successful
        """
        cache_path = self._get_cache_path(key)
        
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'value': value
            }
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f)
            
            return True
        
        except Exception as e:
            return False
    
    def delete(self, key: str) -> bool:
        """Delete cache entry"""
        cache_path = self._get_cache_path(key)
        
        try:
            if os.path.exists(cache_path):
                os.remove(cache_path)
            return True
        except:
            return False
    
    def clear_all(self) -> int:
        """Clear all cache. Returns number of files deleted."""
        count = 0
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    os.remove(os.path.join(self.cache_dir, filename))
                    count += 1
        except Exception as e:
            pass
        return count

# Global cache instance
cache = SimpleCache()
