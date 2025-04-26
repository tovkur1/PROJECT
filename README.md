# Инструкция по настройке проекта RIA News Parser

## Требования
- Python 3.8+
- PostgreSQL 12+
- pip

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/ваш-username/ria-news-parser.git
cd ria-news-parser
```

2. Создайте и активируйте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/MacOS
venv\Scripts\activate    # Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Настройка базы данных

1. Установите PostgreSQL (если еще не установлен):
```bash
# Для Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib
```

2. Создайте базу данных и пользователя:
```bash
sudo -u postgres psql
```
```sql
CREATE DATABASE ria_db;
CREATE USER ria_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ria_db TO ria_user;
\q
```

3. Настройте подключение в файле `config.py`:
```python
DB_URI = 'postgresql://ria_user:your_password@localhost/ria_db'
```

## Запуск

1. Запустите парсер:
```bash
python server.py
```

2. После успешного выполнения скрипта данные будут доступны в таблице `ria_data` в PostgreSQL.

## Проверка данных

Вы можете проверить записанные данные с помощью:

1. Командной строки PostgreSQL:
```bash
psql -U ria_user -d ria_db -c "SELECT * FROM ria_data LIMIT 5;"
```

2. Или через DBeaver/другой клиент PostgreSQL.

## Структура базы данных

Таблица `ria_data` содержит следующие поля:
- `id` - первичный ключ (автоинкремент)
- `date` - дата создания записи
- `title` - заголовок новости
- `description` - описание новости
- `lat` - широта
- `lon` - долгота
- `type` - тип события

## Рекомендации для разработки

1. Для production использования добавьте:
   - Обработку ошибок
   - Логирование
   - Регулярный запуск по расписанию (например, через cron)

2. Файл `.env` для хранения чувствительных данных (добавьте его в `.gitignore`):
```
DB_URI=postgresql://username:password@localhost/dbname
```

## Лицензия

Этот проект распространяется под лицензией MIT.
