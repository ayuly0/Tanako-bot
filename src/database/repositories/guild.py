from typing import Optional, Dict, Any
from .base import BaseRepository
from src.models.guild import GuildConfig
from datetime import datetime

class GuildRepository(BaseRepository[GuildConfig]):
    def __init__(self, client):
        super().__init__(client, "guilds")
        self._cache: Dict[int, GuildConfig] = {}
        
    async def get_config(self, guild_id: int) -> Optional[GuildConfig]:
        if guild_id in self._cache:
            return self._cache[guild_id]
        
        result = await self.find_by_id("guild_id", guild_id)
        if not result:
            return None
        
        config = GuildConfig.from_dict({
            'guild_id': result['guild_id'],
            'settings': result.get('settings', {}),
            'created_at': result.get('created_at'),
            'updated_at': result.get('updated_at'),
            'case_counter': result.get('case_counter', 0),
            'ticket_counter': result.get('ticket_counter', 0),
            'filter_rules': result.get('filter_rules', []),
            'custom_commands': result.get('custom_commands', {})
        })
        self._cache[guild_id] = config
        return config
    
    async def save_config(self, config: GuildConfig):
        config.updated_at = datetime.now()
        data = {
            'guild_id': config.guild_id,
            'settings': config.settings.to_dict(),
            'created_at': config.created_at.isoformat() if config.created_at else datetime.now().isoformat(),
            'updated_at': config.updated_at.isoformat(),
            'case_counter': config.case_counter,
            'ticket_counter': config.ticket_counter,
            'filter_rules': config.filter_rules,
            'custom_commands': config.custom_commands
        }
        
        existing = await self.find_by_id("guild_id", config.guild_id)
        if existing:
            await self.update(data, {"guild_id": config.guild_id})
        else:
            await self.insert(data)
        
        self._cache[config.guild_id] = config
