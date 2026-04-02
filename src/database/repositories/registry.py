from .user import UserRepository, LevelRepository
from .guild import GuildRepository
from .moderation import ModerationRepository
from .support import TicketRepository, MetricRepository
from .utility import UtilityRepository
from src.database.engine.ws_client import DatabaseClient

class RepositoryRegistry:
    def __init__(self, db_uri: str):
        self.client = DatabaseClient(uri=db_uri)
        self.users = UserRepository(self.client)
        self.levels = LevelRepository(self.client)
        self.guilds = GuildRepository(self.client)
        self.moderation = ModerationRepository(self.client)
        self.tickets = TicketRepository(self.client)
        self.metrics = MetricRepository(self.client)
        self.utility = UtilityRepository(self.client)
        
    async def initialize(self):
        await self.client.connect()
        
    async def close(self):
        await self.client.disconnect()
