import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from weather_api import get_weather
from notification import send_notification
import logging

# Конфигурация
API_KEY = "6596f316a56103539735bd87c6246997"  # Замените на ваш ключ OpenWeatherMap
DB_NAME = "weather.db"


def init_db():
    """Инициализация базы данных с двумя таблицами: cities и weather."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS cities (
            city_id INTEGER PRIMARY KEY AUTOINCREMENT,
            city_name TEXT NOT NULL UNIQUE
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS weather (
            weather_id INTEGER PRIMARY KEY AUTOINCREMENT,
            city_id INTEGER,
            temperature REAL,
            description TEXT,
            timestamp TEXT,
            FOREIGN KEY (city_id) REFERENCES cities (city_id)
        )
    """
    )

    conn.commit()
    conn.close()


def add_weather(city: str, tree: ttk.Treeview, status_label: tk.Label):
    """Добавление или обновление данных о погоде для города."""
    if not city:
        status_label.config(text="Ошибка: Введите название города")
        return

    weather_data = get_weather(city, API_KEY)
    if not weather_data or "error" in weather_data:
        status_label.config(
            text=f"Ошибка: {weather_data.get('error', 'Неизвестная ошибка')}"
        )
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Проверяем, есть ли город в базе
    cursor.execute(
        "SELECT city_id FROM cities WHERE city_name = ?", (weather_data["city"],)
    )
    city_record = cursor.fetchone()

    if city_record:
        city_id = city_record[0]
    else:
        cursor.execute(
            "INSERT INTO cities (city_name) VALUES (?)", (weather_data["city"],)
        )
        city_id = cursor.lastrowid

    # Проверяем, есть ли запись о погоде
    cursor.execute("SELECT weather_id FROM weather WHERE city_id = ?", (city_id,))
    weather_record = cursor.fetchone()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if weather_record:
        cursor.execute(
            """
            UPDATE weather 
            SET temperature = ?, description = ?, timestamp = ?
            WHERE city_id = ?
        """,
            (
                weather_data["temperature"],
                weather_data["description"],
                timestamp,
                city_id,
            ),
        )
    else:
        cursor.execute(
            """
            INSERT INTO weather (city_id, temperature, description, timestamp)
            VALUES (?, ?, ?, ?)
        """,
            (
                city_id,
                weather_data["temperature"],
                weather_data["description"],
                timestamp,
            ),
        )

    conn.commit()
    conn.close()

    status_label.config(text=f"Данные для {weather_data['city']} сохранены")
    refresh_tree(tree)


def refresh_tree(tree: ttk.Treeview):
    """Обновление таблицы с данными о погоде."""
    for item in tree.get_children():
        tree.delete(item)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT c.city_name, w.temperature, w.description, w.timestamp
        FROM weather w
        JOIN cities c ON w.city_id = c.city_id
    """
    )

    for row in cursor.fetchall():
        tree.insert("", tk.END, values=row)

    conn.close()


def search_weather(city: str, tree: ttk.Treeview, status_label: tk.Label):
    """Поиск погоды по названию города."""
    for item in tree.get_children():
        tree.delete(item)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT c.city_name, w.temperature, w.description, w.timestamp
        FROM weather w
        JOIN cities c ON w.city_id = c.city_id
        WHERE c.city_name LIKE ?
    """,
        (f"%{city}%",),
    )

    records = cursor.fetchall()
    if not records:
        status_label.config(text=f"Данные для города {city} не найдены")
    else:
        for row in records:
            tree.insert("", tk.END, values=row)
        status_label.config(text="Поиск завершен")

    conn.close()


def delete_weather(city: str, tree: ttk.Treeview, status_label: tk.Label):
    """Удаление данных о погоде для города."""
    if not city:
        status_label.config(text="Ошибка: Введите название города")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT city_id FROM cities WHERE city_name = ?", (city,))
    city_record = cursor.fetchone()

    if not city_record:
        status_label.config(text=f"Город {city} не найден")
        conn.close()
        return

    city_id = city_record[0]

    cursor.execute("DELETE FROM weather WHERE city_id = ?", (city_id,))
    cursor.execute("DELETE FROM cities WHERE city_id = ?", (city_id,))

    conn.commit()
    conn.close()

    status_label.config(text=f"Данные для города {city} удалены")
    refresh_tree(tree)


def create_gui():
    """Создание графического интерфейса."""
    window = tk.Tk()
    window.title("Погода")
    window.geometry("600x400")

    # Поле ввода города
    tk.Label(window, text="Название города:").pack(pady=5)
    city_entry = tk.Entry(window)
    city_entry.pack()

    # Таблица для отображения данных
    columns = ("Город", "Температура (°C)", "Описание", "Время")
    tree = ttk.Treeview(window, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120)
    tree.pack(pady=10, fill=tk.BOTH, expand=True)

    # Статусная строка
    status_label = tk.Label(window, text="Готово", fg="blue")
    status_label.pack()

    # Кнопки
    btn_frame = tk.Frame(window)
    btn_frame.pack(pady=5)

    tk.Button(
        btn_frame,
        text="Добавить/Обновить",
        command=lambda: add_weather(city_entry.get(), tree, status_label),
    ).pack(side=tk.LEFT, padx=5)
    tk.Button(
        btn_frame,
        text="Поиск",
        command=lambda: search_weather(city_entry.get(), tree, status_label),
    ).pack(side=tk.LEFT, padx=5)
    tk.Button(
        btn_frame,
        text="Удалить",
        command=lambda: delete_weather(city_entry.get(), tree, status_label),
    ).pack(side=tk.LEFT, padx=5)
    tk.Button(
        btn_frame, text="Обновить таблицу", command=lambda: refresh_tree(tree)
    ).pack(side=tk.LEFT, padx=5)

    # Инициализация базы данных и начальное обновление таблицы
    init_db()
    refresh_tree(tree)

    window.mainloop()


def fetch_and_notify(city: str, api_key: str) -> bool:
    """Получает данные и отправляет уведомление."""
    try:
        data = get_weather(city, api_key)
        if not data:
            return False
        return send_notification(data)
    except Exception as e:
        logging.error(f"Ошибка в fetch_and_notify: {e}")
        return False


if __name__ == "__main__":
    create_gui()
