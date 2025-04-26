from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import requests
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ria_user:your_password@localhost/ria_db'
db = SQLAlchemy(app)

class RiaData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    title = db.Column(db.String(500))
    description = db.Column(db.Text)
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    type = db.Column(db.String(100))

# Получаем данные
api_url = "https://cdndc.img.ria.ru/dc/kay-n/2022/SOP-content/data/points/data-24.04.2025.json?v=1196"
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "Referer": "https://ria.ru/20220622/spetsoperatsiya-1795199102.html"
}
data = requests.get(api_url, headers=headers).json()

# Выводим все записи в консоль
print("Все полученные записи:")
for item in data:
    print(item)

# Записываем в БД
for item in data:
    new_entry = RiaData(
        date=datetime.strptime(item['date'], '%d.%m.%Y'),
        title=item['title'],
        description=item.get('description', ''),
        lat=float(item['lat']),
        lon=float(item['lon']),
        type=item.get('type', '')
    )
    db.session.add(new_entry)

db.session.commit()
print(f"\nЗаписано {len(data)} записей в базу данных")
