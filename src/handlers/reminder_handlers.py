from typing import Dict, List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from src.services.db_service import DatabaseService
from src.utils.logger import log_user_action, log_error

# Inicializamos el servicio de base de datos
db_service = DatabaseService()

# Estados para la conversación
SELECTING_REMINDER_ACTION, SETTING_REMINDER_TIMES = range(2)

# Opciones horarias predefinidas
REMINDER_TIMES = [
    "07:00", "08:00", "09:00", 
    "12:00", "13:00", "14:00", 
    "18:00", "19:00", "20:00"
]

async def reminders_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Manejador para el comando /recordatorios"""
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
        
        # Guardar la configuración actual de recordatorios
        context.user_data["current_reminders"] = db_user.reminder_settings
        
        # Verificar si los recordatorios están habilitados
        is_enabled = db_user.reminder_settings.get("enabled", False)
        
        # Crear teclado inline con opciones
        keyboard = [
            [
                InlineKeyboardButton(
                    "✅ Desactivar recordatorios" if is_enabled else "✅ Activar recordatorios", 
                    callback_data="rem_toggle"
                )
            ],
            [InlineKeyboardButton("⏰ Configurar horarios", callback_data="rem_times")],
            [InlineKeyboardButton("❌ Cancelar", callback_data="rem_cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        current_times = db_user.reminder_settings.get("times", [])
        times_str = ", ".join(current_times) if current_times else "No configurados"
        
        status = "Activados" if is_enabled else "Desactivados"
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Configuración actual de recordatorios:\n\n"
                 f"Estado: {status}\n"
                 f"Horarios: {times_str}\n\n"
                 f"¿Qué te gustaría hacer?",
            reply_markup=reply_markup
        )
        
        log_user_action(user.id, "accedió a configuración de recordatorios")
        return SELECTING_REMINDER_ACTION
        
    except Exception as e:
        log_error(f"Error al acceder a recordatorios para usuario {user.id}", e)
        await context.bot.send_message(
            chat_id=chat_id,
            text="Lo siento, hubo un problema al acceder a los recordatorios. Por favor, intenta de nuevo más tarde."
        )
        return ConversationHandler.END

async def handle_reminder_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Maneja la selección de acción para recordatorios"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    
    if query.data == "rem_cancel":
        await query.edit_message_text(text="Configuración de recordatorios cancelada.")
        return ConversationHandler.END
    
    elif query.data == "rem_toggle":
        # Cambiar el estado de los recordatorios
        if "current_reminders" not in context.user_data:
            context.user_data["current_reminders"] = {"enabled": False, "times": []}
        
        is_currently_enabled = context.user_data["current_reminders"].get("enabled", False)
        context.user_data["current_reminders"]["enabled"] = not is_currently_enabled
        
        # Guardar en la base de datos
        db_service.update_user_reminders(user.id, context.user_data["current_reminders"])
        
        new_status = "activados" if not is_currently_enabled else "desactivados"
        await query.edit_message_text(
            text=f"Tus recordatorios han sido {new_status}."
        )
        
        log_user_action(user.id, f"recordatorios {new_status}")
        return ConversationHandler.END
    
    elif query.data == "rem_times":
        # Configurar horarios de recordatorios
        current_times = context.user_data.get("current_reminders", {}).get("times", [])
        
        keyboard = []
        for time in REMINDER_TIMES:
            is_selected = time in current_times
            text = f"✅ {time}" if is_selected else time
            keyboard.append([InlineKeyboardButton(text, callback_data=f"time_{time}")])
        
        keyboard.append([InlineKeyboardButton("✅ Guardar", callback_data="time_save")])
        keyboard.append([InlineKeyboardButton("❌ Cancelar", callback_data="rem_cancel")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text="Selecciona los horarios para tus recordatorios (puedes elegir varios):",
            reply_markup=reply_markup
        )
        
        return SETTING_REMINDER_TIMES
    
    return ConversationHandler.END

async def handle_reminder_times(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Maneja la selección de horarios para recordatorios"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    
    if query.data == "rem_cancel":
        await query.edit_message_text(text="Configuración de recordatorios cancelada.")
        return ConversationHandler.END
    
    elif query.data == "time_save":
        # Guardar horarios en la base de datos
        if "current_reminders" not in context.user_data:
            context.user_data["current_reminders"] = {"enabled": True, "times": []}
        
        # Activar recordatorios si se seleccionaron horarios
        if context.user_data["current_reminders"].get("times", []):
            context.user_data["current_reminders"]["enabled"] = True
        
        db_service.update_user_reminders(user.id, context.user_data["current_reminders"])
        
        times_str = ", ".join(context.user_data["current_reminders"].get("times", [])) or "No seleccionados"
        await query.edit_message_text(
            text=f"Tus horarios de recordatorios han sido guardados: {times_str}"
        )
        
        log_user_action(user.id, "actualizó horarios de recordatorios")
        return ConversationHandler.END
    
    else:
        # Actualizar la selección de horarios
        time = query.data.replace("time_", "")
        
        if "current_reminders" not in context.user_data:
            context.user_data["current_reminders"] = {"enabled": True, "times": []}
        
        current_times = context.user_data["current_reminders"].get("times", [])
        
        # Alternar selección
        if time in current_times:
            current_times.remove(time)
        else:
            current_times.append(time)
        
        context.user_data["current_reminders"]["times"] = current_times
        
        # Actualizar teclado
        keyboard = []
        for t in REMINDER_TIMES:
            is_selected = t in current_times
            text = f"✅ {t}" if is_selected else t
            keyboard.append([InlineKeyboardButton(text, callback_data=f"time_{t}")])
        
        keyboard.append([InlineKeyboardButton("✅ Guardar", callback_data="time_save")])
        keyboard.append([InlineKeyboardButton("❌ Cancelar", callback_data="rem_cancel")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text="Selecciona los horarios para tus recordatorios (puedes elegir varios):",
            reply_markup=reply_markup
        )
        
        return SETTING_REMINDER_TIMES