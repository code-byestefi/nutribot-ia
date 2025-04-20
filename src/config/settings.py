import os
from dotenv import load_dotenv

# variables de .env
load_dotenv()

# config de las variables de entorno 

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("No se ha especificado el token de telegram en las variables de entorno")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError("No se ha espeficiado la clave API de Anthropic en el archivo .env")

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/nutribot")


DEFAULT_TIMEZONE = "America/Argentina/Buenos_Aires"