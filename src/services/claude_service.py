import json
from typing import Dict, List, Optional
import anthropic
from anthropic import Anthropic

from src.config.settings import ANTHROPIC_API_KEY
from src.utils.logger import log_info, log_error

class ClaudeService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ClaudeService, cls).__new__(cls)
            cls._instance.client = Anthropic(api_key=ANTHROPIC_API_KEY)
        return cls._instance

    def analyze_meal(self, meal_text: str, user_preferences: Dict) -> Dict:
        try:
            # Construir el prompt para Claude
            prompt = self._build_meal_analysis_prompt(meal_text, user_preferences)
            
            # Llamar a la API de Claude
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                system="Eres un asistente nutricional experto. Analiza las comidas y proporciona información nutricional precisa y recomendaciones basadas en las preferencias del usuario.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            # Parsear la respuesta
            try:
                # Intentar extraer un JSON de la respuesta
                content = response.content[0].text
                # Buscar si hay un bloque JSON en la respuesta
                if "```json" in content and "```" in content.split("```json", 1)[1]:
                    json_str = content.split("```json", 1)[1].split("```", 1)[0].strip()
                    return json.loads(json_str)
                else:
                    # Si no hay JSON, crear una estructura simplificada basada en el texto
                    return {
                        "foods": self._extract_foods(content),
                        "nutrients": self._extract_nutrients(content),
                        "summary": content.split("\n\n")[0] if "\n\n" in content else content[:200]
                    }
            except Exception as e:
                log_error(f"Error al parsear la respuesta de Claude: {str(e)}")
                # Devolver un formato simplificado con el texto completo
                return {
                    "raw_analysis": response.content[0].text,
                    "error_parsing": True
                }
                
        except Exception as e:
            log_error(f"Error al llamar a la API de Claude: {str(e)}")
            return {
                "error": str(e),
                "foods": [],
                "nutrients": {}
            }
    
    def generate_recommendations(self, recent_meals: List[Dict], user_preferences: Dict) -> str:
        """
        Genera recomendaciones personalizadas basadas en las comidas recientes
        
        Args:
            recent_meals: Lista de comidas recientes con sus análisis
            user_preferences: Preferencias del usuario
            
        Returns:
            Texto con recomendaciones personalizadas
        """
        try:
            # Construir el prompt para Claude
            prompt = self._build_recommendations_prompt(recent_meals, user_preferences)
            
            # Llamar a la API de Claude
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1500,
                system="Eres un asistente nutricional experto. Genera recomendaciones nutricionales personalizadas basadas en el historial de comidas y las preferencias del usuario.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text
                
        except Exception as e:
            log_error(f"Error al generar recomendaciones: {str(e)}")
            return "No se pudieron generar recomendaciones en este momento. Por favor, intenta de nuevo más tarde."
        
    def _build_meal_analysis_prompt(self, meal_text: str, user_preferences: Dict) -> str:
        """Construye el prompt para el análisis de comidas"""
        dietary_restrictions = user_preferences.get("dietary_restrictions", [])
        goals = user_preferences.get("goals", [])
        
        prompt = f"""Eres un asistente nutricional experto. Analiza la siguiente comida registrada por un usuario y proporciona:
            1. Un breve análisis nutricional
            2. Identificación de alimentos consumidos y su clasificación
            3. Evaluación de nutrientes (proteínas, carbohidratos, grasas, fibra)

            Comida registrada: {meal_text}

            El usuario tiene las siguientes preferencias:
            - Restricciones dietéticas: {', '.join(dietary_restrictions) if dietary_restrictions else 'Ninguna'}
            - Objetivos: {', '.join(goals) if goals else 'No especificados'}

            Por favor, proporciona tu análisis en formato JSON con esta estructura:
            ```json
            {{
            "foods": ["alimento1", "alimento2", ...],
            "nutrients": {{
                "protein": "nivel",
                "carbs": "nivel",
                "fats": "nivel",
                "fiber": "nivel"
            }},
            "summary": "Breve análisis nutricional de la comida"
            }}
            """
        return prompt
    
    def _build_recommendations_prompt(self, recent_meals: List[Dict], user_preferences: Dict) -> str:
        """Construye el prompt para generar recomendaciones"""
        dietary_restrictions = user_preferences.get("dietary_restrictions", [])
        goals = user_preferences.get("goals", [])
        
        meals_text = "\n".join([
            f"- {meal.get('meal_type', 'Comida')}: {meal.get('text', 'No especificado')}" 
            for meal in recent_meals
        ])
        
        prompt = f"""Eres un asistente nutricional experto. Genera recomendaciones personalizadas basadas en el historial de comidas recientes de un usuario.
            Comidas recientes: {meals_text}
            El usuario tiene las siguientes preferencias:
            Restricciones dietéticas: {', '.join(dietary_restrictions) if dietary_restrictions else 'Ninguna'}
            Objetivos: {', '.join(goals) if goals else 'No especificados'}

            Por favor, proporciona:

            Una evaluación general del patrón alimenticio actual
            3-5 recomendaciones específicas para mejorar la alimentación considerando las preferencias del usuario
            Sugerencias de alimentos que podrían incorporar en su dieta

            Usa un tono amable y motivador.
            """
        return prompt
    
    def _extract_foods(self, text: str) -> List[str]:
        """Extrae lista de alimentos del texto cuando no hay JSON"""
        # Implementación simple para extraer alimentos mencionados
        common_foods = ["huevos", "tostada", "pan", "café", "leche", "ensalada", "atún", 
                        "lechuga", "tomate", "maíz", "galletas", "chocolate", "jugo",
                        "arroz", "pollo", "pescado", "carne", "fruta", "verdura"]
        
        return [food for food in common_foods if food in text.lower()]

    def _extract_nutrients(self, text: str) -> Dict[str, str]:
        """Extrae información de nutrientes del texto cuando no hay JSON"""
        nutrients = {
            "protein": "medio",
            "carbs": "medio",
            "fats": "medio",
            "fiber": "bajo"
        }
        
        # Búsqueda simple de menciones de niveles de nutrientes
        if "proteína alta" in text.lower() or "alto en proteína" in text.lower():
            nutrients["protein"] = "alto"
        elif "proteína baja" in text.lower() or "bajo en proteína" in text.lower():
            nutrients["protein"] = "bajo"
            
        if "carbohidratos altos" in text.lower() or "alto en carbohidratos" in text.lower():
            nutrients["carbs"] = "alto"
        elif "carbohidratos bajos" in text.lower() or "bajo en carbohidratos" in text.lower():
            nutrients["carbs"] = "bajo"
            
        if "grasas altas" in text.lower() or "alto en grasas" in text.lower():
            nutrients["fats"] = "alto"
        elif "grasas bajas" in text.lower() or "bajo en grasas" in text.lower():
            nutrients["fats"] = "bajo"
            
        if "fibra alta" in text.lower() or "alto en fibra" in text.lower():
            nutrients["fiber"] = "alto"
        elif "fibra baja" in text.lower() or "bajo en fibra" in text.lower():
            nutrients["fiber"] = "bajo"
        
        return nutrients