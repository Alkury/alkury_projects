# Telegram Bot for Donations

Этот проект представляет собой Telegram-бота, который позволяет пользователям делать пожертвования в виде "звёзд". Бот использует библиотеку `aiogram` для асинхронной работы с Telegram API.

## Установка:

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/Fedor-777/alkury_projects.git
   cd alkury_projects
   ```
2. **Создайте виртуальное окружение (рекомендуется):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Для Linux/Mac
   venv\Scripts\activate  # Для Windows
   ```
   
3. **Установите зависимости:**
   Убедитесь, что у вас установлен pip, затем выполните:
   ```bash
   pip install -r requirements.txt
   ```
## Команды:

```
/start - Начать взаимодействие с ботом.
/paysupport - Получить информацию о пожертвованиях.
/gift - подарить подарок по id и по id подарка
   пример:
      - /gift
      - 5895603153683874485 1075370548 1 ( след сообщение)
/gift_premium - отрпавить прем на несколько месяцев (3, 6, 12)
   пример:
      - /gift_premium
      - 1075370548 3 (след сообщение)

```
