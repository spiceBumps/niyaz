import requests
import logging
from typing import Dict, Optional

# Настройка логгирования
logging.basicConfig(
    filename="error.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def get_weather(city: str, api_key: str) -> Optional[Dict]:
    """
    Получает данные о погоде для указанного города через OpenWeatherMap API.
    Возвращает словарь с городом, температурой и описанием.
    """
    if not city:
        logging.error("Пустое название города")
        raise ValueError("Название города не может быть пустым")
    
    if not api_key:
        logging.error("Пустой API-ключ")
        raise ValueError("API-ключ не может быть пустым")
    
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        return {
            "city": data["name"],
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"]
        }
    except requests.exceptions.HTTPError as http_err:
        error_msg = f"HTTP ошибка при запросе погоды для {city}: {http_err}"
        logging.error(error_msg)
        raise
    except requests.exceptions.ConnectionError as conn_err:
        error_msg = f"Ошибка соединения при запросе погоды для {city}: {conn_err}"
        logging.error(error_msg)
        raise
    except requests.exceptions.RequestException as req_err:
        error_msg = f"Ошибка запроса для {city}: {req_err}"
        logging.error(error_msg)
        raise