# server.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import requests
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/ria_data'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class RiaData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(100))
    
    def __repr__(self):
        return f'<RiaData {self.title}>'

def fetch_ria_data():
    api_url = "https://cdndc.img.ria.ru/dc/kay-n/2022/SOP-content/data/points/data-24.04.2025.json?v=1196"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "Referer": "https://ria.ru/20220622/spetsoperatsiya-1795199102.html"
    }
    
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

@app.route('/parse-and-save')
def parse_and_save():
    data = fetch_ria_data()
    if not data:
        return "Failed to fetch data", 500
    
    try:
        for item in data:
            # Преобразуем дату из строки в объект datetime
            date_obj = datetime.strptime(item['date'], '%d.%m.%Y')
            
            # Создаем новую запись
            new_entry = RiaData(
                date=date_obj,
                title=item['title'],
                description=item.get('description', ''),
                lat=float(item['lat']),
                lon=float(item['lon']),
                type=item.get('type', '')
            )
            
            db.session.add(new_entry)
        
        db.session.commit()
        return f"Successfully saved {len(data)} records", 200
    except Exception as e:
        db.session.rollback()
        return f"Error saving data: {str(e)}", 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
