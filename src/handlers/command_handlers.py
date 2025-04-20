from telegram import Update
from telegram.ext import ContextTypes

from src.services.db_service import DatabaseService
from src.models.user import User
from src.utils.logger import log_user_action, log_info, log_error


from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler

# Inicializamos el servicio de base de datos
db_service = DatabaseService()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manejador del comando /start"""
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    try:
        # Registramos o actualizamos el usuario en la base de datos
        db_user = User(
            telegram_id=user.id,
            username=user.username or "",
            first_name=user.first_name
        )
        db_service.save_user(db_user)
        
        # Mensaje de bienvenida
        welcome_message = (
            f"👋 ¡Hola {user.first_name}! Soy NutriBot, tu asistente personal de nutrición.\n\n"
            "Puedo ayudarte a registrar tus comidas, analizar su valor nutricional y "
            "ofrecerte recomendaciones personalizadas.\n\n"
            "Para comenzar, simplemente cuéntame lo que has comido y yo lo analizaré. "
            "También puedes usar los siguientes comandos:\n\n"
            "/ayuda - Ver todos los comandos disponibles\n"
            "/preferencias - Configurar tus preferencias alimenticias\n"
            "/recordatorios - Configurar recordatorios para registrar tus comidas\n"
            "/resumen - Ver un resumen de tus comidas del día actual"
        )
        
        await context.bot.send_message(chat_id=chat_id, text=welcome_message)
        log_user_action(user.id, "inicio bot")
        
    except Exception as e:
        error_message = "Lo siento, ha ocurrido un error al iniciar. Por favor, intenta de nuevo más tarde."
        await context.bot.send_message(chat_id=chat_id, text=error_message)
        log_error(f"Error en comando start para usuario {user.id}", e)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manejador del comando /ayuda"""
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    help_message = (
        "🤖 *Comandos disponibles:*\n\n"
        "/start - Iniciar o reiniciar el bot\n"
        "/ayuda - Mostrar esta guía de ayuda\n"
        "/resumen - Ver resumen de comidas del día\n"
        "/recomendacion - Recibir recomendaciones personalizadas\n"
        "/preferencias - Configurar preferencias alimenticias\n"
        "/recordatorios - Configurar recordatorios\n\n"
        
        "📝 *Cómo usar el bot:*\n"
        "1. Para registrar una comida, simplemente envía un mensaje describiendo lo que comiste\n"
        "2. El bot analizará automáticamente el valor nutricional\n"
        "3. Puedes ver un resumen diario con el comando /resumen\n"
        "4. Configura tus preferencias para obtener recomendaciones más personalizadas\n\n"
        
        "Si tienes alguna pregunta o sugerencia, ¡no dudes en contactarnos!"
    )
    
    await context.bot.send_message(chat_id=chat_id, text=help_message, parse_mode="Markdown")
    log_user_action(user.id, "solicitó ayuda")

async def preferences_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manejador para el comando /preferencias"""
    # Este es un placeholder - implementaremos esto completamente más adelante
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    await context.bot.send_message(
        chat_id=chat_id, 
        text="Próximamente podrás configurar tus preferencias alimenticias aquí. Esta función está en desarrollo."
    )
    log_user_action(user.id, "intentó acceder a preferencias")

async def reminders_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manejador para el comando /recordatorios"""
    # Este es un placeholder - implementaremos esto completamente más adelante
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    await context.bot.send_message(
        chat_id=chat_id, 
        text="Próximamente podrás configurar recordatorios aquí. Esta función está en desarrollo."
    )
    log_user_action(user.id, "intentó acceder a recordatorios")

async def summary_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manejador para el comando /resumen"""
    # Este es un placeholder - implementaremos esto completamente más adelante
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    await context.bot.send_message(
        chat_id=chat_id, 
        text="Próximamente podrás ver un resumen de tus comidas aquí. Esta función está en desarrollo."
    )
    log_user_action(user.id, "intentó acceder a resumen")

async def recommendation_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manejador para el comando /recomendacion"""
    # Este es un placeholder - implementaremos esto completamente más adelante
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    await context.bot.send_message(
        chat_id=chat_id, 
        text="Próximamente podrás recibir recomendaciones personalizadas aquí. Esta función está en desarrollo."
    )
    log_user_action(user.id, "intentó acceder a recomendaciones")



# Constantes para el ConversationHandler
SELECTING_PREFERENCE, ADDING_RESTRICTION, ADDING_GOAL = range(3)

async def preferences_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Manejador para el comando /preferencias"""
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    try:
        # Obtener usuario de la base de datos
        db_user = db_service.get_user(user.id)
        if not db_user:
            await context.bot.send_message(
                chat_id=chat_id,
                text="Por favor, inicia el bot primero con el comando /start"
            )
            return ConversationHandler.END
        
        # Crear teclado inline con opciones
        keyboard = [
            [
                InlineKeyboardButton("Restricciones dietéticas", callback_data="pref_restrictions"),
                InlineKeyboardButton("Objetivos nutricionales", callback_data="pref_goals")
            ],
                [InlineKeyboardButton("Cancelar", callback_data="pref_cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Guardar las preferencias actuales en el contexto para referencia
        context.user_data["current_preferences"] = db_user.preferences
        
        # Enviar mensaje con opciones
        await context.bot.send_message(
            chat_id=chat_id,
            text="¿Qué preferencias te gustaría configurar?",
            reply_markup=reply_markup
        )
        
        log_user_action(user.id, "accedió a preferencias")
        return SELECTING_PREFERENCE
        
    except Exception as e:
        log_error(f"Error al acceder a preferencias para usuario {user.id}", e)
        await context.bot.send_message(
            chat_id=chat_id,
            text="Lo siento, hubo un problema al acceder a las preferencias. Por favor, intenta de nuevo más tarde."
        )
        return ConversationHandler.END