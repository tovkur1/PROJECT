from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import requests
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ria_user:your_password@localhost/ria_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class RiaData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    title = db.Column(db.String(500))
    description = db.Column(db.Text)
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    type = db.Column(db.String(100))

def main():
    # Создаем таблицу, если ее нет
    with app.app_context():
        db.create_all()
    
    # Получаем данные
    api_url = "https://cdndc.img.ria.ru/dc/kay-n/2022/SOP-content/data/points/data-24.04.2025.json?v=1196"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "Referer": "https://ria.ru/20220622/spetsoperatsiya-1795199102.html"
    }
    
    try:
        print("Получение данных с API...")
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        print(f"Получено {len(data)} записей")
        print("Пример записи:", data[0])  # Выводим первую запись для проверки
        
        # Записываем в БД
        with app.app_context():
            for item in data:
                # Создаем запись с текущей датой (так как в API нет поля date)
                new_entry = RiaData(
                    date=datetime.now(),  # Используем текущую дату/время
                    title=item.get('name', 'Без названия'),  # 'name' -> 'title'
                    description=item.get('text', ''),  # 'text' -> 'description'
                    lat=float(item.get('lat', 0)),
                    lon=float(item.get('lng', 0)),  # 'lng' -> 'lon'
                    type=item.get('type', 'неизвестно')
                )
                db.session.add(new_entry)
            
            db.session.commit()
            print(f"Успешно записано {len(data)} записей в таблицу ria_data")
            
            # Проверяем записанные данные
            count = RiaData.query.count()
            print(f"Всего записей в таблице: {count}")
            
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        if 'db' in locals():
            db.session.rollback()

if __name__ == '__main__':
    main()
