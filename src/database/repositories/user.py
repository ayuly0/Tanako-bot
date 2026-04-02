from typing import Optional, List, Dict, Any
from .base import BaseRepository
from src.models.user import UserData
from datetime import datetime

class UserRepository(BaseRepository[UserData]):
    def __init__(self, client):
        super().__init__(client, "users")
        self._cache: Dict[str, UserData] = {}
        
    async def get_user_data(self, user_id: int, guild_id: int) -> Optional[UserData]:
        cache_key = f"{guild_id}_{user_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        result = await self.find_by_id("id", cache_key)
        if not result:
            return None
        
        user_data = UserData.from_dict(result.get('data', {
            'user_id': user_id,
            'guild_id': guild_id
        }))
        self._cache[cache_key] = user_data
        return user_data
    
    async def save_user_data(self, user_data: UserData):
        cache_key = f"{user_data.guild_id}_{user_data.user_id}"
        data = {
            'id': cache_key,
            'user_id': user_data.user_id,
            'guild_id': user_data.guild_id,
            'data': user_data.to_dict(),
            'updated_at': datetime.now().isoformat()
        }
        
        existing = await self.find_by_id("id", cache_key)
        if existing:
            await self.update(data, {"id": cache_key})
        else:
            await self.insert(data)
        
        self._cache[cache_key] = user_data

class LevelRepository(BaseRepository[Dict]):
    def __init__(self, client):
        super().__init__(client, "user_levels")
        self._cache: Dict[str, Dict] = {}
        
    async def get_user_level(self, user_id: int, guild_id: int) -> Optional[Dict[str, Any]]:
        level_key = f"{guild_id}_{user_id}"
        if level_key in self._cache:
            return self._cache[level_key]
        
        result = await self.find_by_id("id", level_key)
        if result:
            self._cache[level_key] = result
        return result
    
    async def save_level(self, data: Dict[str, Any]):
        level_key = data['id']
        existing = await self.find_by_id("id", level_key)
        if existing:
            await self.update(data, {"id": level_key})
        else:
            await self.insert(data)
        self._cache[level_key] = data

    async def get_leaderboard(self, guild_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        return await self.select(
            conditions={'guild_id': guild_id},
            order_by=[('total_xp', 'DESC')],
            limit=limit
        )
