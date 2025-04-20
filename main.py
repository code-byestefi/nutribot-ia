import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from src.config.settings import TELEGRAM_TOKEN
from src.handlers.command_handlers import (
    start_command, help_command, preferences_command,
    reminders_command, summary_command, recommendation_command
)
from src.handlers.message_handlers import handle_message
from src.utils.logger import log_info

def main() -> None:
    """Función principal que inicia el bot"""
    # Configurar logging
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )
    
    log_info("Iniciando NutriBot...")
    
    # Crear la aplicación
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Registrar manejadores de comandos
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("ayuda", help_command))
    application.add_handler(CommandHandler("preferencias", preferences_command))
    application.add_handler(CommandHandler("recordatorios", reminders_command))
    application.add_handler(CommandHandler("resumen", summary_command))
    application.add_handler(CommandHandler("recomendacion", recommendation_command))
    
    # Registrar manejador de mensajes de texto
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Iniciar el bot
    log_info("NutriBot está en funcionamiento!")
    application.run_polling()

if __name__ == "__main__":
    main()