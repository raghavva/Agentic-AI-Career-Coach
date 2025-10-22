import redis
import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os

class CacheManager:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=0,
            decode_responses=True
        )
        self.cache_ttl = int(os.getenv('CACHE_TTL_HOURS', 24)) * 3600  # Convert to seconds
    
    def _generate_key(self, career_goal: str, missing_skills: list) -> str:
        """Generate a unique cache key"""
        key_data = f"{career_goal}:{':'.join(sorted(missing_skills))}"
        return f"careerpath:{hashlib.md5(key_data.encode()).hexdigest()}"
    
    def get_cached_courses(self, career_goal: str, missing_skills: list) -> Optional[Dict[str, Any]]:
        """Retrieve cached course data"""
        key = self._generate_key(career_goal, missing_skills)
        try:
            cached_data = self.redis_client.get(key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            print(f"Cache get error: {e}")
        return None
    
    def set_cached_courses(self, career_goal: str, missing_skills: list, courses: list, recommendations: dict):
        """Store course data in cache"""
        key = self._generate_key(career_goal, missing_skills)
        cache_data = {
            'courses': courses,
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat(),
            'career_goal': career_goal,
            'missing_skills': missing_skills
        }
        try:
            self.redis_client.setex(key, self.cache_ttl, json.dumps(cache_data))
            print(f"Cached courses for {career_goal}")
        except Exception as e:
            print(f"Cache set error: {e}")
    
    def invalidate_cache(self, career_goal: str = None):
        """Clear cache entries"""
        try:
            if career_goal:
                pattern = f"careerpath:*{hashlib.md5(career_goal.encode()).hexdigest()[:8]}*"
            else:
                pattern = "careerpath:*"
            
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
                print(f"Cleared {len(keys)} cache entries")
        except Exception as e:
            print(f"Cache invalidation error: {e}")

    def _generate_career_key(self, career_goal: str) -> str:
        """Generate cache key based only on career goal"""
        key_data = f"{career_goal}"
        return f"careerpath:{hashlib.md5(key_data.encode()).hexdigest()}"

    def get_cached_courses_by_career(self, career_goal: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached course data by career goal only"""
        key = self._generate_career_key(career_goal)        
        try:
            cached_data = self.redis_client.get(key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            print(f"Cache get error: {e}")
        return None

    def set_cached_courses_by_career(self, career_goal: str, courses: list, recommendations: dict):
        """Store course data in cache by career goal only"""
        key = self._generate_career_key(career_goal)
        cache_data = {
            'courses': courses,
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat(),
            'career_goal': career_goal
        }
        try:
            self.redis_client.setex(key, self.cache_ttl, json.dumps(cache_data))
            print(f"Cached courses for career: {career_goal}")
        except Exception as e:
            print(f"Cache set error: {e}")

# Fallback to in-memory cache if Redis unavailable
class InMemoryCacheManager:
    def __init__(self):
        self.cache = {}
        self.cache_ttl = timedelta(hours=24)
    
    def _generate_key(self, career_goal: str, missing_skills: list) -> str:
        key_data = f"{career_goal}:{':'.join(sorted(missing_skills))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get_cached_courses(self, career_goal: str, missing_skills: list) -> Optional[Dict[str, Any]]:
        key = self._generate_key(career_goal, missing_skills)
        if key in self.cache:
            cached_data = self.cache[key]
            if datetime.now() - cached_data['timestamp'] < self.cache_ttl:
                return cached_data
            else:
                del self.cache[key]  # Remove expired entry
        return None
    
    def set_cached_courses(self, career_goal: str, missing_skills: list, courses: list, recommendations: dict):
        key = self._generate_key(career_goal, missing_skills)
        self.cache[key] = {
            'courses': courses,
            'recommendations': recommendations,
            'timestamp': datetime.now(),
            'career_goal': career_goal,
            'missing_skills': missing_skills
        }

# Initialize cache manager
try:
    cache_manager = CacheManager()
    print("Using Redis cache")
except:
    cache_manager = InMemoryCacheManager()
    print("Using in-memory cache")