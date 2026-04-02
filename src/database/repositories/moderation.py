from typing import Optional, List, Dict, Any
from .base import BaseRepository
from src.models.moderation import ModerationCase, ModerationAction
from datetime import datetime

class ModerationRepository(BaseRepository[ModerationCase]):
    def __init__(self, client):
        super().__init__(client, "moderation_cases")
        
    async def get_case(self, guild_id: int, case_id: int) -> Optional[ModerationCase]:
        result = await self.find_one({'guild_id': guild_id, 'case_id': case_id})
        if not result:
            return None
        
        case_data = result.get('data', {})
        case_data.update({
            'case_id': result['case_id'],
            'guild_id': result['guild_id'],
            'target_id': result['target_id'],
            'moderator_id': result['moderator_id'],
            'action': result['action'],
            'reason': result['reason'],
            'created_at': result.get('created_at'),
            'expires_at': result.get('expires_at'),
            'duration_seconds': result.get('duration_seconds'),
            'is_active': result.get('is_active', True),
            'revoked': result.get('revoked', False)
        })
        return ModerationCase.from_dict(case_data)
    
    async def get_user_cases(self, guild_id: int, user_id: int) -> List[ModerationCase]:
        results = await self.select(conditions={
            'guild_id': guild_id,
            'target_id': user_id
        })
        
        cases = []
        for result in results:
            case_data = result.get('data', {})
            case_data.update({
                'case_id': result['case_id'],
                'guild_id': result['guild_id'],
                'target_id': result['target_id'],
                'moderator_id': result['moderator_id'],
                'action': result['action'],
                'reason': result['reason'],
                'created_at': result.get('created_at'),
                'is_active': result.get('is_active', True)
            })
            cases.append(ModerationCase.from_dict(case_data))
        
        return sorted(cases, key=lambda c: c.case_id, reverse=True)
    
    async def save_case(self, case: ModerationCase):
        data = {
            'id': f"{case.guild_id}_{case.case_id}",
            'case_id': case.case_id,
            'guild_id': case.guild_id,
            'target_id': case.target_id,
            'moderator_id': case.moderator_id,
            'action': case.action.value,
            'reason': case.reason,
            'created_at': case.created_at.isoformat() if case.created_at else datetime.now().isoformat(),
            'expires_at': case.expires_at.isoformat() if case.expires_at else None,
            'duration_seconds': case.duration_seconds,
            'is_active': case.is_active,
            'revoked': case.revoked,
            'data': case.to_dict()
        }
        
        existing = await self.find_by_id("id", data['id'])
        if existing:
            await self.update(data, {"id": data['id']})
        else:
            await self.insert(data)
