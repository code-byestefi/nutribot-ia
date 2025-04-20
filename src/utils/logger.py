import logging
import os
from datetime import datetime

# Configuración básica del logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Mostrar logs en consola
    ]
)

# Crear un logger personalizado para nuestra aplicación
logger = logging.getLogger('nutribot')

def log_info(message: str) -> None:
    """Registra un mensaje de información"""
    logger.info(message)

def log_error(message: str, error: Exception = None) -> None:
    """Registra un mensaje de error"""
    if error:
        logger.error(f"{message}: {str(error)}")
    else:
        logger.error(message)

def log_user_action(telegram_id: int, action: str, details: str = None) -> None:
    """Registra una acción de usuario"""
    message = f"Usuario {telegram_id} - {action}"
    if details:
        message += f": {details}"
    logger.info(message)

def log_meal_record(telegram_id: int, meal_type: str, content: str) -> None:
    """Registra el registro de una comida"""
    shortened_content = content[:50] + "..." if len(content) > 50 else content
    logger.info(f"Usuario {telegram_id} registró {meal_type}: {shortened_content}")