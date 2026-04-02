from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class DatabaseSettings(BaseSettings):
    host: str = Field(default="0.0.0.0", alias="DB_API_HOST")
    port: int = Field(default=8080, alias="DB_API_PORT")
    uri: str = Field(default="ws://localhost:8080", alias="DB_API_URI")
    data_dir: str = Field(default="data/kotonexus_takako", alias="DB_DATA_DIR")
    cluster_enabled: bool = Field(default=False, alias="DB_CLUSTER_ENABLED")
    node_id: Optional[str] = Field(default=None, alias="DB_NODE_ID")
    seed_nodes: Optional[str] = Field(default=None, alias="DB_SEED_NODES")
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

class BotSettings(BaseSettings):
    token: str = Field(..., alias="DISCORD_TOKEN")
    shard_count: Optional[int] = Field(default=None, alias="SHARD_COUNT")
    shard_ids: Optional[str] = Field(default=None, alias="SHARD_IDS")
    debug: bool = Field(default=False, alias="DEBUG")
    version: str = "2.1.0"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

class Config:
    def __init__(self):
        self.db = DatabaseSettings()
        self.bot = BotSettings()

# Global config instance
config = Config()
