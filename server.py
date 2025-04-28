from flask import Flask, jsonify
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

@app.route('/api/ria-data', methods=['GET'])
def get_ria_data():
    data_entries = RiaData.query.all()
    data_list = [{
        'id': entry.id,
        'date': entry.date.strftime("%Y-%m-%d %H:%M:%S"),
        'title': entry.title,
        'description': entry.description,
        'lat': entry.lat,
        'lon': entry.lon,
        'type': entry.type
    } for entry in data_entries]
    return jsonify(data_list)

def main():
    with app.app_context():
        db.create_all()
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
            print("Пример записи:", data[0])

            for item in data:
                new_entry = RiaData(
                    date=datetime.now(),
                    title=item.get('name', 'Без названия'),
                    description=item.get('text', ''),
                    lat=float(item.get('lat', 0)),
                    lon=float(item.get('lng', 0)),
                    type=item.get('type', 'неизвестно')
                )
                db.session.add(new_entry)
            db.session.commit()
            print(f"Успешно записано {len(data)} записей в таблицу ria_data")
            count = RiaData.query.count()
            print(f"Всего записей в таблице: {count}")

        except Exception as e:
            print(f"Ошибка: {str(e)}")
            if 'db' in locals():
                db.session.rollback()

if __name__ == '__main__':
    main()
    app.run(debug=True)
