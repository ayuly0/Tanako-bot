import os
import sys
import unittest
import asyncio
from unittest.mock import AsyncMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set dummy env vars for testing
os.environ['DISCORD_TOKEN'] = 'dummy_token_for_testing'

from src.database.repositories.registry import RepositoryRegistry
from src.core.config import config
from src.models.user import UserData, UserStats
from src.models.guild import GuildConfig

class TestRepositoryRegistry(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # We'll use the RepositoryRegistry with its intended configuration
        self.registry = RepositoryRegistry(config.db.uri)
        
        # Bypass connection checks in ws_client.py
        self.registry.client.connected = True
        self.registry.client.connect = AsyncMock()
        self.registry.client.disconnect = AsyncMock()
        
        # Mock ALL client CRUD methods to avoid hitting real networking
        self.registry.client.find_by_id = AsyncMock(return_value=None)
        self.registry.client.select = AsyncMock(return_value=[])
        self.registry.client.insert = AsyncMock(return_value={'status': 'ok'})
        self.registry.client.update = AsyncMock(return_value={'status': 'ok'})
        self.registry.client.delete = AsyncMock(return_value={'status': 'ok'})
        
    async def test_registry_initialization(self):
        """Check if registry correctly initializes its internal client."""
        # Reset connected for this specific test to check call
        self.registry.client.connected = False 
        await self.registry.initialize()
        self.registry.client.connect.assert_called_once()
        await self.registry.close()
        self.registry.client.disconnect.assert_called_once()
        
    async def test_user_repository_mapping(self):
        """Verify that UserRepository calls its internal client as expected."""
        self.registry.client.find_by_id.return_value = None
        
        user_data = await self.registry.users.get_user_data(12345, 67890)
        self.assertIsNone(user_data)
        self.registry.client.find_by_id.assert_called_once()
            
    async def test_guild_repository_mapping(self):
        """Verify that GuildRepository calls its internal client as expected."""
        self.registry.client.select.return_value = []
        
        # GuildRepository.get_config calls find_by_id then select/insert depending on logic
        # but let's just check it calls the client at least once
        guild_config = await self.registry.guilds.get_config(67890)
        self.assertIsNone(guild_config)
        self.assertTrue(self.registry.client.find_by_id.called or self.registry.client.select.called)
            
    async def test_utility_repository_secret_chat_integration(self):
        """Verify UtilityRepository secret chat identity logic."""
        self.registry.client.find_by_id.return_value = {'user_id': 12345, 'nickname': 'TestGhost'}
        
        secret_user = await self.registry.utility.get_secret_user(12345)
        self.assertIsNotNone(secret_user)
        self.assertEqual(secret_user['nickname'], 'TestGhost')
        self.registry.client.find_by_id.assert_called_with('secret_users', 'user_id', 12345)

if __name__ == '__main__':
    unittest.main()
