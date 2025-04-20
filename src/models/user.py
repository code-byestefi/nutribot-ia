from datetime import datetime
from typing import List, Dict, Optional

class User:
    def __init__(
        self,
        telegram_id: int,
        username: str,
        first_name: str,
        timezone: str = "America/Argentina/Buenos_Aires",
        preferences: Optional[Dict] = None,
        reminder_settings: Optional[Dict] = None,
        created_at: Optional[datetime] = None
    ):
        self.telegram_id = telegram_id
        self.username = username
        self.first_name = first_name
        self.timezone = timezone
        self.preferences = preferences or {
            "dietary_restrictions": [],
            "goals": []
        }
        self.reminder_settings = reminder_settings or {
            "enabled": False,
            "times": []
        }
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self) -> Dict:
        """Convierte el objeto usuario a un diccionario para almacenar en MongoDB"""
        return {
            "telegram_id": self.telegram_id,
            "username": self.username,
            "first_name": self.first_name,
            "timezone": self.timezone,
            "preferences": self.preferences,
            "reminder_settings": self.reminder_settings,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data:Dict) -> 'User':
        """Crea un objeto User que viene desde la base de datos MongoDB"""
        return cls(
            telegram_id=data["telegram_id"],
            username=data["username"],
            first_name=data["first_name"],
            timezone=data["timezone"],
            preferences=data["preferences"],
            reminder_settings=data["reminder_settings"],
            created_at=data["created_at"]
        )
