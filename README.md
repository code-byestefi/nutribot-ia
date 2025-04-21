# NutriBot-IA

Bot de Telegram para seguimiento nutricional con análisis de IA mediante Anthropic Claude.

## Descripción

NutriBot-IA es un asistente nutricional personal que se integra con Telegram para ayudarte a registrar y analizar tus comidas diarias. Utilizando la potencia de la IA de Claude (Anthropic), el bot proporciona análisis nutricionales, recomendaciones personalizadas y recordatorios para mejorar tus hábitos alimenticios.

## Características principales

- 📝 **Registro de comidas**: Simplemente envía un mensaje describiendo lo que comiste y el bot lo analizará automáticamente
- 🔍 **Análisis nutricional**: Recibe información sobre los nutrientes de tus comidas (proteínas, carbohidratos, grasas, fibra)
- 📊 **Resumen diario**: Visualiza un resumen de todas tus comidas del día y su balance nutricional
- 🧠 **Recomendaciones personalizadas**: Obtén sugerencias basadas en tu historial de alimentación y objetivos
- ⏰ **Recordatorios configurables**: Establece horarios para recibir recordatorios de tus comidas
- ⚙️ **Preferencias personalizadas**: Configura restricciones dietéticas y objetivos nutricionales

## Tecnologías utilizadas

- Python 3.8+
- python-telegram-bot: Framework para la API de Telegram
- Anthropic Claude API: Análisis nutricional mediante IA
- MongoDB: Almacenamiento de datos de usuarios y comidas
- APScheduler: Programación de recordatorios
- PyTZ: Manejo de zonas horarias

## Instalación y configuración

### Requisitos previos

- Python 3.8 o superior
- Cuenta en Telegram
- Token de Bot de Telegram (obtenido de @BotFather)
- Clave API de Anthropic Claude
- MongoDB (local o en la nube)

### Pasos de instalación

1. Clona este repositorio:

git clone https://github.com/TU-USUARIO/nutribot-ia.git
cd nutribot-ia

2. Crea un entorno virtual e instala las dependencias:
python -m venv venv

En Windows:
venv\Scripts\activate
En macOS/Linux:
source venv/bin/activate
pip install -r requirements.txt

3. Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:
Token de Telegram Bot
TELEGRAM_TOKEN=tu_token_de_telegram_aquí
API Key de Anthropic
ANTHROPIC_API_KEY=tu_clave_api_anthropic_aquí
Conexión a MongoDB
MONGODB_URI=mongodb://localhost:27017/nutribot

4. Inicia el bot:
python main.py

## Uso

1. Busca tu bot en Telegram por su nombre de usuario
2. Inicia una conversación con el comando `/start`
3. Configura tus preferencias con `/preferencias`
4. Establece recordatorios con `/recordatorios` si lo deseas
5. Envía mensajes describiendo tus comidas para recibir análisis
6. Consulta el resumen del día con `/resumen`
7. Obtén recomendaciones personalizadas con `/recomendacion`

## Comandos disponibles

- `/start` - Iniciar o reiniciar el bot
- `/ayuda` - Mostrar la guía de ayuda
- `/preferencias` - Configurar preferencias alimenticias
- `/recordatorios` - Configurar recordatorios de comidas
- `/resumen` - Ver un resumen de las comidas del día
- `/recomendacion` - Recibir recomendaciones personalizadas

## Estructura del proyecto
├── main.py                # Punto de entrada principal
├── requirements.txt       # Dependencias del proyecto
├── .env                   # Variables de entorno (no incluido en el repositorio)
├── src/                   # Código fuente
│   ├── config/            # Configuraciones
│   ├── handlers/          # Manejadores de comandos y mensajes
│   ├── models/            # Modelos de datos
│   ├── services/          # Servicios (DB, Claude, Scheduler)
│   └── utils/             # Utilidades


## Contribuciones

Las contribuciones son bienvenidas. Si encuentras un bug o tienes una idea para mejorar el bot, no dudes en abrir un issue o enviar un pull request.

