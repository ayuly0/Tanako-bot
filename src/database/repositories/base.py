from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Generic, TypeVar
from src.database.engine.ws_client import DatabaseClient

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    """Abstract Base Class for all Repositories."""
    
    def __init__(self, client: DatabaseClient, table_name: str):
        self.client = client
        self.table_name = table_name
    
    async def find_by_id(self, id_column: str, id_value: Any) -> Optional[Dict[str, Any]]:
        return await self.client.find_by_id(self.table_name, id_column, id_value)
    
    async def find_one(self, conditions: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self.client.find_one(self.table_name, conditions)
    
    async def select(
        self, 
        conditions: Optional[Dict[str, Any]] = None,
        order_by: Optional[List[tuple]] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        return await self.client.select(
            self.table_name, 
            conditions=conditions or {},
            order_by=order_by,
            limit=limit
        )
    
    async def insert(self, data: Dict[str, Any]) -> str:
        return await self.client.insert(self.table_name, data)
    
    async def update(self, data: Dict[str, Any], conditions: Dict[str, Any]) -> int:
        return await self.client.update(self.table_name, data, conditions)
    
    async def delete(self, conditions: Dict[str, Any]) -> int:
        return await self.client.delete(self.table_name, conditions)
