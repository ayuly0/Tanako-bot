from typing import Optional, List, Dict, Any
from .base import BaseRepository
from src.models.filter import FilterConfig
from src.models.logs import LogConfig
from datetime import datetime
import uuid

class UtilityRepository(BaseRepository[Dict]):
    def __init__(self, client):
        super().__init__(client, "utility")
        self._cache: Dict[str, Any] = {}
        
    async def get_filter_config(self, guild_id: int) -> Optional[FilterConfig]:
        result = await self.client.find_by_id("filters", 'guild_id', guild_id)
        if not result:
            return None
        return FilterConfig.from_dict(result.get('data', {'guild_id': guild_id}))
    
    async def save_filter_config(self, config: FilterConfig):
        data = {
            'guild_id': config.guild_id,
            'data': config.to_dict(),
            'updated_at': datetime.now().isoformat()
        }
        existing = await self.client.find_by_id("filters", 'guild_id', config.guild_id)
        if existing:
            await self.client.update("filters", data, {'guild_id': config.guild_id})
        else:
            await self.client.insert("filters", data)

    async def get_log_config(self, guild_id: int) -> Optional[LogConfig]:
        result = await self.client.find_by_id("log_configs", 'guild_id', guild_id)
        if not result:
            return None
        return LogConfig.from_dict(result.get('data', {'guild_id': guild_id}))
    
    async def save_log_config(self, config: LogConfig):
        data = {
            'guild_id': config.guild_id,
            'data': config.to_dict(),
            'updated_at': datetime.now().isoformat()
        }
        existing = await self.client.find_by_id("log_configs", 'guild_id', config.guild_id)
        if existing:
            await self.client.update("log_configs", data, {'guild_id': config.guild_id})
        else:
            await self.client.insert("log_configs", data)

    async def get_secret_user(self, user_id: int) -> Optional[Dict]:
        return await self.client.find_by_id("secret_users", 'user_id', user_id)

    async def get_secret_user_by_nickname(self, nickname: str) -> Optional[Dict]:
        results = await self.client.select("secret_users", conditions={'nickname': nickname})
        return results[0] if results else None
    
    async def save_secret_user(self, user_id: int, nickname: str):
        data = {
            'user_id': user_id,
            'nickname': nickname,
            'is_active': True,
            'updated_at': datetime.now().isoformat()
        }
        existing = await self.get_secret_user(user_id)
        if existing:
            await self.client.update("secret_users", data, {'user_id': user_id})
        else:
            await self.client.insert("secret_users", data)

    async def delete_secret_user(self, user_id: int):
        await self.client.delete("secret_users", {'user_id': user_id})

    async def create_secret_chat(self, sender_id: int, receiver_id: int) -> str:
        chat_id = str(uuid.uuid4())
        data = {
            'id': chat_id,
            'sender_id': sender_id,
            'receiver_id': receiver_id,
            'created_at': int(datetime.now().timestamp() * 1000)
        }
        await self.client.insert("secret_chats", data)
        return chat_id

    async def get_host_checks(self, guild_id: Optional[int] = None) -> List[Dict]:
        conditions = {'is_active': True}
        if guild_id:
            conditions['guild_id'] = guild_id
        return await self.client.select("host_checks", conditions=conditions)
    
    async def save_host_check(self, data: Dict):
        existing = await self.client.find_by_id("host_checks", "id", data['id'])
        if existing:
            await self.client.update("host_checks", data, {'id': data['id']})
        else:
            await self.client.insert("host_checks", data)

    async def save_metric(self, shard_id: int, metric_type: str, value: float, data: Dict[str, Any]):
        metric_data = {
            'shard_id': shard_id,
            'metric_type': metric_type,
            'value': value,
            'metadata': data,
            'timestamp': datetime.now().isoformat()
        }
        await self.client.insert("metrics", metric_data)

    async def get_metrics(self, shard_id: int, limit: int = 100) -> List[Dict]:
        return await self.client.select("metrics", conditions={'shard_id': shard_id}, limit=limit)

    async def get_all_active_host_checks(self) -> List[Dict]:
        return await self.client.select("host_checks", conditions={'is_active': True})

    async def update_host_check_status(self, check_id: str, status: str):
        await self.client.update("host_checks", {'last_status': status, 'last_check': datetime.now().isoformat()}, {'id': check_id})

    async def delete_host_check(self, check_id: str):
        await self.client.delete("host_checks", {'id': check_id})

    async def get_all_node_status(self) -> List[Dict]:
        # Typically sourced from a global metrics/nodes table
        return await self.client.select("nodes", conditions={})

    async def save_node_status(self, shard_id: int, status: str, latency: float, guild_count: int, memory_mb: float):
        data = {
            'shard_id': shard_id,
            'status': status,
            'latency': latency,
            'guild_count': guild_count,
            'memory_mb': memory_mb,
            'updated_at': datetime.now().isoformat()
        }
        existing = await self.client.find_by_id("nodes", "shard_id", shard_id)
        if existing:
            await self.client.update("nodes", data, {'shard_id': shard_id})
        else:
            await self.client.insert("nodes", data)
