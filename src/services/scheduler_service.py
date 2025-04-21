import asyncio
from datetime import datetime, time
from typing import Dict, List, Optional
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from telegram import Bot

from src.config.settings import TELEGRAM_TOKEN
from src.services.db_service import DatabaseService
from src.utils.logger import log_info, log_error

db_service = DatabaseService()

class SchedulerService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SchedulerService, cls).__new__(cls)
            # Usar BackgroundScheduler en lugar de AsyncIOScheduler
            cls._instance.scheduler = BackgroundScheduler()
            cls._instance.scheduler.add_jobstore(MemoryJobStore())
            cls._instance.bot = Bot(TELEGRAM_TOKEN)
            cls._instance.initialized = False
        return cls._instance
    
    def start(self):
        """Inicia el planificador de tareas"""
        if not self.initialized:
            # Comentamos la inicialización del planificador por ahora
            # self.scheduler.start()
            self.initialized = True
            log_info("Planificador de tareas (modo simulado)")
    
    def schedule_reminders(self):
        """Programa los recordatorios para todos los usuarios"""
        # Esta funcionalidad está temporalmente deshabilitada
        log_info("Recordatorios programados para 0 usuarios (modo simulado)")
    
    def _schedule_user_reminder(self, user_id: int, time_str: str, timezone_str: str):
        """Programa un recordatorio para un usuario específico"""
        try:
            # Parsear hora
            hour, minute = map(int, time_str.split(':'))
            
            # Crear trigger con zona horaria
            trigger = CronTrigger(
                hour=hour,
                minute=minute,
                timezone=pytz.timezone(timezone_str)
            )
            
            # Programar tarea
            job_id = f"reminder_{user_id}_{time_str.replace(':', '')}"
            self.scheduler.add_job(
                self._send_reminder,
                trigger=trigger,
                id=job_id,
                replace_existing=True,
                args=[user_id]
            )
            
            log_info(f"Recordatorio programado: usuario {user_id}, hora {time_str}, zona {timezone_str}")
            
        except Exception as e:
            log_error(f"Error al programar recordatorio para usuario {user_id}: {str(e)}", e)
    
    async def _send_reminder(self, user_id: int):
        """Envía un recordatorio a un usuario"""
        try:
            # Determinar el tipo de comida basado en la hora local del usuario
            user = db_service.get_user(user_id)
            if not user:
                return
            
            timezone = pytz.timezone(user.timezone)
            current_time = datetime.now(timezone)
            hour = current_time.hour
            
            # Determinar tipo de comida
            if 5 <= hour < 11:
                meal_type = "desayuno"
            elif 11 <= hour < 15:
                meal_type = "almuerzo"
            elif 15 <= hour < 18:
                meal_type = "merienda"
            else:
                meal_type = "cena"
            
            # Construir mensaje
            message = (
                f"⏰ *Recordatorio de alimentación*\n\n"
                f"Es hora de tu {meal_type}. ¿Qué vas a comer? "
                f"Cuéntame para analizar su valor nutricional."
            )
            
            # Enviar mensaje
            await self.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode="Markdown"
            )
            
            log_info(f"Recordatorio enviado a usuario {user_id}")
            
        except Exception as e:
            log_error(f"Error al enviar recordatorio a usuario {user_id}: {str(e)}", e)

