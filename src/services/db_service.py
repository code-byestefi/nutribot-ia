from typing import List, Dict, Optional, Any
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from src.config.settings import MONGODB_URI
from src.models.user import User
from src.models.meal import Meal

"""operaciones de bd. Patron Singleton para una unica conexion a la base de datos"""
class DatabaseService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseService, cls).__new__(cls)
            cls._instance.client = MongoClient(MONGODB_URI)
            cls._instance.db = cls._instance.client.get_database()
            cls._instance._init_collections()
        return cls._instance

    def _init_collections(self):
        """Inicializa las colecciones de la base de datos"""
        self.users_collection = self.db.users
        self.meals_collection = self.db.meals

    # Métodos para usuarios
    def save_user(self, user: User) -> str:
        """Guarda un usuario en la base de datos"""
        user_dict = user.to_dict()
        result = self.users_collection.update_one(
            {"telegram_id": user.telegram_id},
            {"$set": user_dict},
            upsert=True
        )
        return str(result.upserted_id) if result.upserted_id else str(user.telegram_id)

    def get_user(self, telegram_id: int) -> Optional[User]:
        """Recupera un usuario por su ID de Telegram"""
        user_data = self.users_collection.find_one({"telegram_id": telegram_id})
        return User.from_dict(user_data) if user_data else None

    def update_user_preferences(self, telegram_id: int, preferences: Dict) -> bool:
        """Actualiza las preferencias de un usuario"""
        result = self.users_collection.update_one(
            {"telegram_id": telegram_id},
            {"$set": {"preferences": preferences}}
        )
        return result.modified_count > 0

    def update_user_reminders(self, telegram_id: int, reminder_settings: Dict) -> bool:
        """Actualiza la configuración de recordatorios de un usuario"""
        result = self.users_collection.update_one(
            {"telegram_id": telegram_id},
            {"$set": {"reminder_settings": reminder_settings}}
        )
        return result.modified_count > 0

    # Métodos para comidas
    def save_meal(self, meal: Meal) -> str:
        """Guarda una comida en la base de datos"""
        meal_dict = meal.to_dict()
        result = self.meals_collection.insert_one(meal_dict)
        return str(result.inserted_id)

    def update_meal_analysis(self, meal_id: str, analysis: Dict) -> bool:
        """Actualiza el análisis de una comida"""
        result = self.meals_collection.update_one(
            {"_id": meal_id},
            {
                "$set": {
                    "analyzed": True,
                    "analysis": analysis
                }
            }
        )
        return result.modified_count > 0

    def get_meals_by_user_and_date(self, telegram_id: int, start_date, end_date) -> List[Meal]:
        """Obtiene las comidas de un usuario en un rango de fechas"""
        meals_data = self.meals_collection.find({
            "telegram_id": telegram_id,
            "timestamp": {"$gte": start_date, "$lte": end_date}
        }).sort("timestamp", 1)
        
        return [Meal.from_dict(meal_data) for meal_data in meals_data]

    def get_recent_meals(self, telegram_id: int, limit: int = 5) -> List[Meal]:
        """Obtiene las comidas más recientes de un usuario"""
        meals_data = self.meals_collection.find(
            {"telegram_id": telegram_id}
        ).sort("timestamp", -1).limit(limit)
        
        return [Meal.from_dict(meal_data) for meal_data in meals_data]
    

    def get_users_with_active_reminders(self) -> List[Dict]:
        # Obtener todos los usuarios con recordatorios activos
        users_data = self.users_collection.find({
            "reminder_settings.enabled": True,
            "reminder_settings.times": {"$exists": True, "$ne": []}
        })
        
        return list(users_data)