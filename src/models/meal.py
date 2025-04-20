from datetime import datetime
from typing import List, Dict, Optional

class Meal:
    def __init__(
        self,
        telegram_id: int,
        text: str,
        meal_type: str,
        timestamp: Optional[datetime] = None,
        analyzed: bool = False,
        analysis: Optional[Dict] = None
    ):
        self.telegram_id = telegram_id
        self.text = text
        self.meal_type = meal_type
        self.timestamp = timestamp or datetime.utcnow()
        self.analyzed = analyzed
        self.analysis = analysis or {}

    def to_dict(self) -> Dict:
        """Convierte el objeto comida a un diccionario para almacenar en MongoDB"""
        return {
            "telegram_id": self.telegram_id,
            "text": self.text,
            "meal_type": self.meal_type,
            "timestamp": self.timestamp,
            "analyzed": self.analyzed,
            "analysis": self.analysis
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Meal':
        """Crea un objeto Meal desde un diccionario de MongoDB"""
        return cls(
            telegram_id=data["telegram_id"],
            text=data["text"],
            meal_type=data["meal_type"],
            timestamp=data["timestamp"],
            analyzed=data["analyzed"],
            analysis=data["analysis"]
        )