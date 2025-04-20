import logging
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ConversationHandler, CallbackQueryHandler
)

from src.config.settings import TELEGRAM_TOKEN
from src.handlers.command_handlers import (
    start_command, help_command, preferences_command,
    summary_command, recommendation_command
)
from src.handlers.message_handlers import handle_message
from src.handlers.preference_handlers import (
    preference_selection, handle_restriction_selection, handle_goal_selection,
    SELECTING_PREFERENCE, ADDING_RESTRICTION, ADDING_GOAL
)
from src.handlers.reminder_handlers import (
    reminders_command, handle_reminder_action, handle_reminder_times,
    SELECTING_REMINDER_ACTION, SETTING_REMINDER_TIMES
)
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
    
    # Registrar manejadores de comandos simples
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("ayuda", help_command))
    application.add_handler(CommandHandler("resumen", summary_command))
    application.add_handler(CommandHandler("recomendacion", recommendation_command))
    
    # Manejador de conversación para preferencias
    preferences_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("preferencias", preferences_command)],
        states={
            SELECTING_PREFERENCE: [CallbackQueryHandler(preference_selection)],
            ADDING_RESTRICTION: [CallbackQueryHandler(handle_restriction_selection)],
            ADDING_GOAL: [CallbackQueryHandler(handle_goal_selection)],
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
    )
    application.add_handler(preferences_conv_handler)
    
    # Manejador de conversación para recordatorios
    reminders_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("recordatorios", reminders_command)],
        states={
            SELECTING_REMINDER_ACTION: [CallbackQueryHandler(handle_reminder_action)],
            SETTING_REMINDER_TIMES: [CallbackQueryHandler(handle_reminder_times)],
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
    )
    application.add_handler(reminders_conv_handler)
    
    # Registrar manejador de mensajes de texto
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Iniciar el bot
    log_info("NutriBot está en funcionamiento!")
    application.run_polling()

if __name__ == "__main__":
    main()