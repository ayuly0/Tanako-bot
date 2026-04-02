"""
Discord Security Bot with Sharding Support
Main entry point for the Discord bot
"""

import os
import sys
import asyncio
import logging
import psutil
from datetime import datetime
from typing import Optional

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

from src.core.config import config
from src.database.repositories.registry import RepositoryRegistry
from src.bot.cogs.utility import WelcomeCog, TicketsCog, LevelingCog, SecretChatCog, HostCheckCog, UtilityCog
from src.bot.cogs.moderation import ModerationCog, AntiNukeCog, AntiRaidCog
from src.bot.cogs.security import FilterCog, AutoModCog
from src.bot.cogs.core import AdminCog, MetricsCog, LoggingCog

os.makedirs('data/logs', exist_ok=True)

logging.basicConfig(
    level=logging.INFO if not config.bot.debug else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('data/logs/bot.log', mode='a', encoding='utf-8')
    ]
)
logger = logging.getLogger('discord_bot')


class SecurityBot(commands.AutoShardedBot):
    def __init__(self, shard_count: Optional[int] = None, shard_ids: Optional[list] = None):
        intents = discord.Intents.all()
        
        super().__init__(
            command_prefix=commands.when_mentioned_or('!'),
            intents=intents,
            help_command=None,
            case_insensitive=True,
            shard_count=shard_count,
            shard_ids=shard_ids
        )
        
        self.registry: RepositoryRegistry = RepositoryRegistry(config.db.uri)
        self.start_time: datetime = datetime.now()
        self.version: str = config.bot.version
        self._metrics_task: Optional[asyncio.Task] = None

    async def setup_hook(self):
        logger.info("Initializing database repositories...")
        await self.registry.initialize()
        logger.info("Database connection established")
        
        logger.info("Loading cogs with dependency injection...")
        cogs = [
            WelcomeCog(self),
            ModerationCog(self),
            TicketsCog(self),
            AntiRaidCog(self),
            AntiNukeCog(self),
            FilterCog(self),
            LoggingCog(self),
            AutoModCog(self),
            AdminCog(self),
            UtilityCog(self),
            LevelingCog(self),
            SecretChatCog(self),
            HostCheckCog(self),
            MetricsCog(self)
        ]
        
        for cog in cogs:
            await self.add_cog(cog)
            logger.info(f"Loaded cog: {cog.__class__.__name__}")
        
        logger.info(f"Loaded {len(self.cogs)} cogs successfully")
        
        logger.info("Syncing slash commands...")
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} slash command(s) globally")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
    
    async def on_ready(self):
        logger.info(f"Bot is ready!")
        if self.user:
            logger.info(f"Logged in as: {self.user} (ID: {self.user.id})")
        
        if self.shard_count:
            logger.info(f"Running with {self.shard_count} shard(s)")
            if self.shard_ids:
                logger.info(f"Shard IDs: {self.shard_ids}")
        
        logger.info(f"Connected to {len(self.guilds)} guild(s)")
        logger.info(f"Discord.py version: {discord.__version__}")
        
        shard_info = ""
        if self.shard_id is not None:
            shard_info = f" | Shard {self.shard_id}"
        
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"{len(self.guilds)} servers{shard_info}"
            ),
            status=discord.Status.online
        )
        
        self._start_heartbeat()
    
    async def _report_shard_status(self, shard_id: int, status: str):
        try:
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            cpu_percent = process.cpu_percent()
            
            shard_guilds = [g for g in self.guilds if g.shard_id == shard_id]
            guild_count = len(shard_guilds)
            member_count = sum(g.member_count or 0 for g in shard_guilds)
            
            uptime = (datetime.now() - self.start_time).total_seconds()
            
            latency = 0.0
            if self.shards and shard_id in self.shards:
                shard = self.shards[shard_id]
                latency = shard.latency * 1000 if shard.latency else 0.0
            
            await self.registry.metrics.save_node_status({
                'shard_id': shard_id,
                'status': status,
                'latency': latency,
                'guild_count': guild_count,
                'member_count': member_count,
                'uptime_seconds': int(uptime),
                'memory_mb': memory_mb,
                'cpu_percent': cpu_percent,
                'version': self.version,
                'last_heartbeat': int(datetime.now().timestamp() * 1000)
            })
        except Exception as e:
            logger.error(f"Failed to report shard status: {e}")
    
    def _start_heartbeat(self):
        @tasks.loop(seconds=30)
        async def heartbeat():
            if self.shard_ids:
                for shard_id in self.shard_ids:
                    await self._report_shard_status(shard_id, "online")
            elif self.shard_id is not None:
                await self._report_shard_status(self.shard_id, "online")
            else:
                await self._report_shard_status(0, "online")
        
        heartbeat.start()
    
    async def on_guild_join(self, guild: discord.Guild):
        logger.info(f"Joined guild: {guild.name} (ID: {guild.id})")
        await self.registry.guilds.get_config(guild.id)
    
    async def close(self):
        logger.info("Shutting down bot...")
        await self.registry.close()
        await super().close()


async def main():
    os.makedirs('data/logs', exist_ok=True)
    os.makedirs('data/db', exist_ok=True)
    
    token = config.bot.token
    if not token or token == "...":
        logger.error("DISCORD_TOKEN not found in environment!")
        sys.exit(1)
    
    bot = SecurityBot(
        shard_count=config.bot.shard_count, 
        shard_ids=[int(i) for i in config.bot.shard_ids.split(",")] if config.bot.shard_ids else None
    )
    
    try:
        await bot.start(token)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        if not bot.is_closed():
            await bot.close()

if __name__ == '__main__':
    asyncio.run(main())
