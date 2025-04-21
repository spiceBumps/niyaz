import logging

# Настройка логгирования
logging.basicConfig(
    filename="error.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def send_notification(weather_data: dict) -> bool:
    """
    Имитирует отправку уведомления о погоде.
    Возвращает True при успехе, иначе вызывает исключение.
    """
    if not weather_data:
        error_msg = "Пустые данные о погоде для отправки уведомления"
        logging.error(error_msg)
        raise ValueError(error_msg)
    
    try:
        # Имитация отправки уведомления
        print(f"Отправлено уведомление: Погода в {weather_data['city']}: "
              f"{weather_data['temperature']}°C, {weather_data['description']}")
        return True
    except KeyError as e:
        error_msg = f"Неверный формат данных о погоде: {e}"
        logging.error(error_msg)
        raise