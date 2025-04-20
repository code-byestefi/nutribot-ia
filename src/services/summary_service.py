from datetime import datetime, time, timedelta
from typing import Dict, List
import pytz

from src.models.meal import Meal
from src.services.db_service import DatabaseService
from src.services.claude_service import ClaudeService
from src.utils.logger import log_info, log_error

db_service = DatabaseService()
claude_service = ClaudeService()

def get_day_summary(telegram_id: int, timezone_str: str = "America/Mexico_City") -> Dict:
    """
    Obtiene un resumen de las comidas del día actual para un usuario
    
    Args:
        telegram_id: ID de Telegram del usuario
        timezone_str: Zona horaria del usuario
        
    Returns:
        Diccionario con el resumen del día
    """
    try:
        # Obtener zona horaria del usuario
        timezone = pytz.timezone(timezone_str)
        
        # Calcular inicio y fin del día en la zona horaria del usuario
        now = datetime.now(timezone)
        start_of_day = timezone.localize(datetime.combine(now.date(), time.min))
        end_of_day = timezone.localize(datetime.combine(now.date(), time.max))
        
        # Convertir a UTC para la consulta a la base de datos
        start_of_day_utc = start_of_day.astimezone(pytz.UTC)
        end_of_day_utc = end_of_day.astimezone(pytz.UTC)
        
        # Obtener las comidas del día
        meals = db_service.get_meals_by_user_and_date(
            telegram_id=telegram_id,
            start_date=start_of_day_utc,
            end_date=end_of_day_utc
        )
        
        # Organizar las comidas por tipo
        meals_by_type = {
            "breakfast": [],
            "lunch": [],
            "dinner": [],
            "snack": []
        }
        
        total_protein = 0
        total_carbs = 0
        total_fats = 0
        total_fiber = 0
        
        # Función para convertir nivel a valor numérico
        def level_to_value(level: str) -> int:
            if level.lower() in ["alto", "high"]:
                return 3
            elif level.lower() in ["medio", "medium"]:
                return 2
            elif level.lower() in ["bajo", "low"]:
                return 1
            return 0
        
        for meal in meals:
            meal_type = meal.meal_type
            if meal_type not in meals_by_type:
                meal_type = "snack"  # Valor por defecto
            
            meals_by_type[meal_type].append(meal)
            
            # Sumar nutrientes si están disponibles
            if meal.analyzed and meal.analysis and "nutrients" in meal.analysis:
                nutrients = meal.analysis["nutrients"]
                total_protein += level_to_value(nutrients.get("protein", "medio"))
                total_carbs += level_to_value(nutrients.get("carbs", "medio"))
                total_fats += level_to_value(nutrients.get("fats", "medio"))
                total_fiber += level_to_value(nutrients.get("fiber", "bajo"))
        
        # Calcular promedio de cada nutriente (si hay comidas)
        num_meals = len(meals)
        if num_meals > 0:
            avg_protein = total_protein / num_meals
            avg_carbs = total_carbs / num_meals
            avg_fats = total_fats / num_meals
            avg_fiber = total_fiber / num_meals
        else:
            avg_protein = avg_carbs = avg_fats = avg_fiber = 0
        
        # Convertir promedio a nivel
        def value_to_level(value: float) -> str:
            if value >= 2.5:
                return "alto"
            elif value >= 1.5:
                return "medio"
            else:
                return "bajo"
        
        # Crear resumen del día
        summary = {
            "date": now.strftime("%d/%m/%Y"),
            "meals_count": num_meals,
            "meals_by_type": {
                "breakfast": len(meals_by_type["breakfast"]),
                "lunch": len(meals_by_type["lunch"]),
                "dinner": len(meals_by_type["dinner"]),
                "snack": len(meals_by_type["snack"])
            },
            "meals_detail": {
                meal_type: [meal.text for meal in meal_list]
                for meal_type, meal_list in meals_by_type.items() if meal_list
            },
            "nutrient_summary": {
                "protein": value_to_level(avg_protein),
                "carbs": value_to_level(avg_carbs),
                "fats": value_to_level(avg_fats),
                "fiber": value_to_level(avg_fiber)
            }
        }
        
        return summary
        
    except Exception as e:
        log_error(f"Error al generar resumen del día para usuario {telegram_id}", e)
        return {
            "error": str(e),
            "meals_count": 0,
            "meals_by_type": {},
            "meals_detail": {},
            "nutrient_summary": {}
        }

def generate_daily_recommendations(telegram_id: int) -> str:
    """
    Genera recomendaciones personalizadas basadas en el resumen del día
    
    Args:
        telegram_id: ID de Telegram del usuario
        
    Returns:
        Texto con recomendaciones personalizadas
    """
    try:
        # Obtener usuario y sus preferencias
        user = db_service.get_user(telegram_id)
        if not user:
            return "No se encontró información del usuario. Por favor, inicia el bot con /start."
        
        # Obtener comidas recientes
        recent_meals = db_service.get_recent_meals(telegram_id, limit=8)
        if not recent_meals:
            return "No hemos registrado comidas suficientes. Registra algunas comidas y luego solicita recomendaciones."
        
        # Convertir las comidas a formato adecuado para Claude
        meals_for_claude = [
            {
                "meal_type": meal.meal_type,
                "text": meal.text,
                "timestamp": meal.timestamp.strftime("%Y-%m-%d %H:%M"),
                "analysis": meal.analysis if meal.analyzed else {}
            }
            for meal in recent_meals
        ]
        
        # Generar recomendaciones usando Claude
        recommendations = claude_service.generate_recommendations(
            recent_meals=meals_for_claude,
            user_preferences=user.preferences
        )
        
        return recommendations
    
    except Exception as e:
        log_error(f"Error al generar recomendaciones para usuario {telegram_id}", e)
        return "Lo siento, no se pudieron generar recomendaciones en este momento. Por favor, intenta de nuevo más tarde."

def format_day_summary(summary: Dict) -> str:
    """
    Formatea el resumen del día para mostrar al usuario
    
    Args:
        summary: Diccionario con el resumen del día
        
    Returns:
        Texto formateado para mostrar al usuario
    """
    if "error" in summary:
        return "No se pudo generar el resumen del día. Por favor, intenta de nuevo más tarde."
    
    meal_type_names = {
        "breakfast": "Desayuno",
        "lunch": "Almuerzo/Comida",
        "dinner": "Cena",
        "snack": "Merienda/Snack"
    }
    
    nutrient_emojis = {
        "protein": "🥩",
        "carbs": "🍚",
        "fats": "🥑",
        "fiber": "🥦"
    }
    
    level_emojis = {
        "alto": "⬆️",
        "medio": "➡️",
        "bajo": "⬇️"
    }
    
    formatted_text = f"📊 *Resumen del día {summary['date']}*\n\n"
    
    if summary["meals_count"] == 0:
        formatted_text += "No has registrado comidas hoy. ¡Empieza a registrar lo que comes para obtener un análisis nutricional!\n"
        return formatted_text
    
    # Comidas por tipo
    formatted_text += "*Comidas registradas:*\n"
    for meal_type, name in meal_type_names.items():
        count = summary["meals_by_type"].get(meal_type, 0)
        if count > 0:
            meals = summary["meals_detail"].get(meal_type, [])
            meals_text = ", ".join(meals[:2])
            if len(meals) > 2:
                meals_text += f" y {len(meals) - 2} más"
            
            formatted_text += f"• {name}: {meals_text}\n"
    
    # Perfil nutricional
    if "nutrient_summary" in summary and summary["nutrient_summary"]:
        formatted_text += "\n*Perfil nutricional del día:*\n"
        
        for nutrient, emoji in nutrient_emojis.items():
            level = summary["nutrient_summary"].get(nutrient, "medio")
            level_emoji = level_emojis.get(level, "➡️")
            
            formatted_text += f"• {emoji} {nutrient.capitalize()}: {level.capitalize()} {level_emoji}\n"
    
    formatted_text += "\nPara recibir recomendaciones personalizadas, usa el comando /recomendacion"
    
    return formatted_text