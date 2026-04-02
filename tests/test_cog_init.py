import os
import sys
import unittest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch

# Ensure src is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.repositories.registry import RepositoryRegistry
from src.bot.cogs.utility import WelcomeCog, TicketsCog, LevelingCog, SecretChatCog, HostCheckCog, UtilityCog
from src.bot.cogs.moderation import ModerationCog, AntiNukeCog, AntiRaidCog
from src.bot.cogs.security import FilterCog, AutoModCog
from src.bot.cogs.core import AdminCog, MetricsCog, LoggingCog

class TestCogInitialization(unittest.TestCase):
    def setUp(self):
        # Mock the Bot
        self.bot = MagicMock()
        
        # Mock tasks.loop to prevent loop start errors
        self.patcher = patch('discord.ext.tasks.loop', lambda **kwargs: lambda func: func)
        self.patcher.start()
        
        # Mock the Registry
        self.registry = MagicMock(spec=RepositoryRegistry)
        self.registry.users = MagicMock()
        self.registry.guilds = MagicMock()
        self.registry.utility = MagicMock()
        self.registry.initialize = AsyncMock()
        
        # Inject registry into bot
        self.bot.registry = self.registry

    def tearDown(self):
        self.patcher.stop()
        
    def test_all_cogs_init(self):
        """Verify that all cogs can be initialized with self.repos."""
        cogs_to_test = [
            WelcomeCog, ModerationCog, TicketsCog, AntiRaidCog, 
            AntiNukeCog, FilterCog, LoggingCog, AutoModCog, 
            AdminCog, UtilityCog, LevelingCog, SecretChatCog, 
            HostCheckCog, MetricsCog
        ]
        
        errors = []
        for cog_class in cogs_to_test:
            try:
                # Patch start() of any task loop inside the cog instance
                with patch('discord.ext.tasks.Loop.start', return_value=None):
                    cog = cog_class(self.bot)
                    self.assertTrue(hasattr(cog, 'repos'), f"Cog {cog_class.__name__} has no 'repos' attribute")
                    self.assertEqual(cog.repos, self.registry, f"Cog {cog_class.__name__} repos attribute mismatch")
                    print(f"✅ {cog_class.__name__} initialized successfully.")
            except Exception as e:
                errors.append(f"❌ {cog_class.__name__} failed: {str(e)}")
        
        if errors:
            self.fail("\n".join(errors))

if __name__ == '__main__':
    unittest.main()
