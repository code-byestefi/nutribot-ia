from typing import Dict, List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from src.services.db_service import DatabaseService
from src.utils.logger import log_user_action, log_error

# Inicializamos el servicio de base de datos
db_service = DatabaseService()

# Estados para la conversación
SELECTING_PREFERENCE, ADDING_RESTRICTION, ADDING_GOAL = range(3)

# Opciones predefinidas
DIETARY_RESTRICTIONS = [
    "vegetariano", "vegano", "sin_gluten", "sin_lactosa", 
    "sin_azúcar", "low_carb", "keto", "paleo"
]

NUTRITIONAL_GOALS = [
    "perder_peso", "ganar_músculo", "mantenimiento", 
    "más_proteína", "más_fibra", "menos_grasas", "control_glucémico"
]

async def preference_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Maneja la selección de tipo de preferencia"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    
    if query.data == "pref_cancel":
        await query.edit_message_text(text="Configuración de preferencias cancelada.")
        return ConversationHandler.END
    
    elif query.data == "pref_restrictions":
        # Preparar teclado con opciones de restricciones dietéticas
        current_restrictions = context.user_data.get("current_preferences", {}).get("dietary_restrictions", [])
        
        keyboard = []
        for restriction in DIETARY_RESTRICTIONS:
            is_selected = restriction in current_restrictions
            text = f"✅ {restriction}" if is_selected else restriction
            keyboard.append([InlineKeyboardButton(text, callback_data=f"rest_{restriction}")])
        
        keyboard.append([InlineKeyboardButton("✅ Guardar", callback_data="rest_save")])
        keyboard.append([InlineKeyboardButton("❌ Cancelar", callback_data="pref_cancel")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text="Selecciona tus restricciones dietéticas (puedes elegir varias):",
            reply_markup=reply_markup
        )
        
        return ADDING_RESTRICTION
    
    elif query.data == "pref_goals":
        # Preparar teclado con opciones de objetivos nutricionales
        current_goals = context.user_data.get("current_preferences", {}).get("goals", [])
        
        keyboard = []
        for goal in NUTRITIONAL_GOALS:
            is_selected = goal in current_goals
            text = f"✅ {goal}" if is_selected else goal
            keyboard.append([InlineKeyboardButton(text, callback_data=f"goal_{goal}")])
        
        keyboard.append([InlineKeyboardButton("✅ Guardar", callback_data="goal_save")])
        keyboard.append([InlineKeyboardButton("❌ Cancelar", callback_data="pref_cancel")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text="Selecciona tus objetivos nutricionales (puedes elegir varios):",
            reply_markup=reply_markup
        )
        
        return ADDING_GOAL
    
    return ConversationHandler.END

async def handle_restriction_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Maneja la selección de restricciones dietéticas"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    
    if query.data == "pref_cancel":
        await query.edit_message_text(text="Configuración de preferencias cancelada.")
        return ConversationHandler.END
    
    elif query.data == "rest_save":
        # Guardar restricciones en la base de datos
        preferences = context.user_data.get("current_preferences", {"dietary_restrictions": [], "goals": []})
        
        db_service.update_user_preferences(user.id, preferences)
        
        await query.edit_message_text(
            text=f"Tus restricciones dietéticas han sido guardadas: {', '.join(preferences.get('dietary_restrictions', []) or ['Ninguna'])}"
        )
        
        log_user_action(user.id, "actualizó restricciones dietéticas")
        return ConversationHandler.END
    
    else:
        # Actualizar la selección de restricciones
        restriction = query.data.replace("rest_", "")
        
        if "current_preferences" not in context.user_data:
            context.user_data["current_preferences"] = {"dietary_restrictions": [], "goals": []}
        
        current_restrictions = context.user_data["current_preferences"].get("dietary_restrictions", [])
        
        # Alternar selección
        if restriction in current_restrictions:
            current_restrictions.remove(restriction)
        else:
            current_restrictions.append(restriction)
        
        context.user_data["current_preferences"]["dietary_restrictions"] = current_restrictions
        
        # Actualizar teclado
        keyboard = []
        for r in DIETARY_RESTRICTIONS:
            is_selected = r in current_restrictions
            text = f"✅ {r}" if is_selected else r
            keyboard.append([InlineKeyboardButton(text, callback_data=f"rest_{r}")])
        
        keyboard.append([InlineKeyboardButton("✅ Guardar", callback_data="rest_save")])
        keyboard.append([InlineKeyboardButton("❌ Cancelar", callback_data="pref_cancel")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text="Selecciona tus restricciones dietéticas (puedes elegir varias):",
            reply_markup=reply_markup
        )
        
        return ADDING_RESTRICTION

async def handle_goal_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Maneja la selección de objetivos nutricionales"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    
    if query.data == "pref_cancel":
        await query.edit_message_text(text="Configuración de preferencias cancelada.")
        return ConversationHandler.END
    
    elif query.data == "goal_save":
        # Guardar objetivos en la base de datos
        preferences = context.user_data.get("current_preferences", {"dietary_restrictions": [], "goals": []})
        
        db_service.update_user_preferences(user.id, preferences)
        
        await query.edit_message_text(
            text=f"Tus objetivos nutricionales han sido guardados: {', '.join(preferences.get('goals', []) or ['Ninguno'])}"
        )
        
        log_user_action(user.id, "actualizó objetivos nutricionales")
        return ConversationHandler.END
    
    else:
        # Actualizar la selección de objetivos
        goal = query.data.replace("goal_", "")
        
        if "current_preferences" not in context.user_data:
            context.user_data["current_preferences"] = {"dietary_restrictions": [], "goals": []}
        
        current_goals = context.user_data["current_preferences"].get("goals", [])
        
        # Alternar selección
        if goal in current_goals:
            current_goals.remove(goal)
        else:
            current_goals.append(goal)
        
        context.user_data["current_preferences"]["goals"] = current_goals
        
        # Actualizar teclado
        keyboard = []
        for g in NUTRITIONAL_GOALS:
            is_selected = g in current_goals
            text = f"✅ {g}" if is_selected else g
            keyboard.append([InlineKeyboardButton(text, callback_data=f"goal_{g}")])
        
        keyboard.append([InlineKeyboardButton("✅ Guardar", callback_data="goal_save")])
        keyboard.append([InlineKeyboardButton("❌ Cancelar", callback_data="pref_cancel")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text="Selecciona tus objetivos nutricionales (puedes elegir varios):",
            reply_markup=reply_markup
        )
        
        return ADDING_GOAL