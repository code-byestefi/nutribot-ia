from datetime import datetime
from typing import Optional, Dict, Any
from telegram import Update
from telegram.ext import ContextTypes

from src.services.db_service import DatabaseService
from src.services.claude_service import ClaudeService
from src.models.meal import Meal
from src.utils.logger import log_meal_record, log_error

# Inicializamos los servicios
db_service = DatabaseService()
claude_service = ClaudeService()

def _detect_meal_type(text: str, time: datetime) -> str:
    """
    Detecta el tipo de comida basado en el texto y la hora
    """
    # Detectar por palabras clave en el texto
    text_lower = text.lower()
    if any(word in text_lower for word in ["desayuno", "desayuné", "breakfast"]):
        return "breakfast"
    elif any(word in text_lower for word in ["almuerzo", "lunch", "comida", "almorcé"]):
        return "lunch"
    elif any(word in text_lower for word in ["cena", "dinner", "cené"]):
        return "dinner"
    elif any(word in text_lower for word in ["snack", "merienda", "bocadillo", "tentempié"]):
        return "snack"
    
    # Si no se encuentra en el texto, intentar inferir por la hora
    hour = time.hour
    if 5 <= hour < 11:
        return "breakfast"
    elif 11 <= hour < 15:
        return "lunch"
    elif 15 <= hour < 18:
        return "snack"
    elif 18 <= hour <= 23 or 0 <= hour < 5:
        return "dinner"
    
    # Valor por defecto
    return "meal"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Maneja los mensajes de texto que describen comidas
    """
    user = update.effective_user
    chat_id = update.effective_chat.id
    message_text = update.message.text
    
    try:
        # Verificar si el usuario existe en la base de datos
        db_user = db_service.get_user(user.id)
        if not db_user:
            # Si no existe, le pedimos que inicie el bot primero
            await context.bot.send_message(
                chat_id=chat_id,
                text="Por favor, inicia el bot primero con el comando /start"
            )
            return
        
        # Enviar mensaje de procesamiento
        await context.bot.send_message(
            chat_id=chat_id,
            text="Estoy analizando tu comida, dame un momento... 🔍"
        )
        
        # Detectar el tipo de comida
        timestamp = datetime.utcnow()
        meal_type = _detect_meal_type(message_text, timestamp)
        
        # Crear y guardar el registro de comida
        meal = Meal(
            telegram_id=user.id,
            text=message_text,
            meal_type=meal_type,
            timestamp=timestamp
        )
        meal_id = db_service.save_meal(meal)
        
        # Registrar en logs
        log_meal_record(user.id, meal_type, message_text)
        
        # Analizar la comida con Claude
        analysis = claude_service.analyze_meal(
            meal_text=message_text,
            user_preferences=db_user.preferences
        )
        
        # Actualizar el análisis en la base de datos
        if meal_id and analysis:
            db_service.update_meal_analysis(meal_id, analysis)
        
        # Preparar y enviar respuesta
        response = _format_meal_analysis_response(meal_type, analysis)
        await context.bot.send_message(
            chat_id=chat_id,
            text=response,
            parse_mode="Markdown"
        )
        
    except Exception as e:
        log_error(f"Error al procesar mensaje para usuario {user.id}", e)
        await context.bot.send_message(
            chat_id=chat_id,
            text="Lo siento, hubo un problema al analizar tu comida. Por favor, intenta de nuevo más tarde."
        )

def _format_meal_analysis_response(meal_type: str, analysis: Dict[str, Any]) -> str:
    """
    Formatea la respuesta del análisis de la comida
    """
    meal_type_names = {
        "breakfast": "Desayuno",
        "lunch": "Almuerzo",
        "dinner": "Cena",
        "snack": "Merienda",
        "meal": "Comida"
    }
    
    meal_name = meal_type_names.get(meal_type, "Comida")
    
    if "error" in analysis:
        return f"No pude analizar completamente tu {meal_name.lower()}. Por favor, intenta de nuevo más tarde."
    
    # Si tenemos un análisis raw, usamos ese
    if "raw_analysis" in analysis:
        return f"*Análisis de tu {meal_name.lower()}*:\n\n{analysis['raw_analysis']}"
    
    # Si tenemos la estructura esperada
    foods = analysis.get("foods", [])
    nutrients = analysis.get("nutrients", {})
    summary = analysis.get("summary", "")
    
    protein_level = nutrients.get("protein", "no determinado")
    carbs_level = nutrients.get("carbs", "no determinado")
    fats_level = nutrients.get("fats", "no determinado")
    fiber_level = nutrients.get("fiber", "no determinado")
    
    response = f"*Análisis de tu {meal_name.lower()}*:\n\n"
    
    if summary:
        response += f"{summary}\n\n"
    
    if foods:
        response += "*Alimentos identificados*:\n"
        for food in foods:
            response += f"• {food}\n"
        response += "\n"
    
    response += "*Perfil nutricional*:\n"
    response += f"• Proteínas: {protein_level}\n"
    response += f"• Carbohidratos: {carbs_level}\n"
    response += f"• Grasas: {fats_level}\n"
    response += f"• Fibra: {fiber_level}\n\n"
    
    response += "💡 *Consejo*: Recuerda que puedes usar /resumen para ver un reporte de todas tus comidas del día."
    
    return response