from typing import Optional, List, Dict, Any
from .base import BaseRepository
from src.models.ticket import Ticket, TicketStatus
from datetime import datetime
import json

class TicketRepository(BaseRepository[Ticket]):
    def __init__(self, client):
        super().__init__(client, "tickets")
        
    async def get_by_channel(self, channel_id: int) -> Optional[Ticket]:
        result = await self.find_one({'channel_id': channel_id})
        if not result:
            return None
        
        ticket_data = result.get('data')
        if ticket_data:
            if isinstance(ticket_data, str):
                try:
                    ticket_data = json.loads(ticket_data)
                except json.JSONDecodeError:
                    ticket_data = None
            if isinstance(ticket_data, dict):
                return Ticket.from_dict(ticket_data)
        
        return None
    
    async def get_user_open_tickets(self, guild_id: int, user_id: int) -> List[Ticket]:
        results = await self.select(conditions={
            'guild_id': guild_id,
            'creator_id': user_id
        })
        
        tickets = []
        for result in results:
            ticket_data = result.get('data')
            if ticket_data:
                if isinstance(ticket_data, str):
                    try:
                        ticket_data = json.loads(ticket_data)
                    except json.JSONDecodeError:
                        ticket_data = None
                if isinstance(ticket_data, dict):
                    ticket = Ticket.from_dict(ticket_data)
                    if ticket.is_open:
                        tickets.append(ticket)
        return tickets
    
    async def save_ticket(self, ticket: Ticket):
        ticket.updated_at = datetime.now()
        data = {
            'ticket_id': ticket.ticket_id,
            'guild_id': ticket.guild_id,
            'channel_id': ticket.channel_id,
            'creator_id': ticket.creator_id,
            'status': ticket.status.value,
            'created_at': ticket.created_at.isoformat() if ticket.created_at else datetime.now().isoformat(),
            'closed_at': ticket.closed_at.isoformat() if ticket.closed_at else None,
            'data': ticket.to_dict()
        }
        
        existing = await self.find_by_id("ticket_id", ticket.ticket_id)
        if existing:
            await self.update(data, {"ticket_id": ticket.ticket_id})
        else:
            await self.insert(data)

class MetricRepository(BaseRepository[Dict]):
    def __init__(self, client):
        super().__init__(client, "metrics")
        
    async def save_metric(self, shard_id: int, metric_type: str, value: float, data: Optional[Dict] = None):
        import uuid
        metric_data = {
            'id': str(uuid.uuid4()),
            'shard_id': shard_id,
            'metric_type': metric_type,
            'value': value,
            'timestamp': int(datetime.now().timestamp() * 1000),
            'data': data or {}
        }
        await self.insert(metric_data)
    
    async def save_node_status(self, data: Dict[str, Any]):
        existing = await self.find_by_id("shard_id", data['shard_id'])
        if existing:
            await self.update(data, {"shard_id": data['shard_id']})
        else:
            await self.insert(data)
