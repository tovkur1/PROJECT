from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

# Настройка логгирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI приложение
app = FastAPI()

# Модель Pydantic для валидации
class Event(BaseModel):
    region: str
    location: str
    latitude: float
    longitude: float
    event_date: str
    description: str

# Подключение к PostgreSQL
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:yourpassword@localhost:5432/ria_events"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Модель SQLAlchemy
class DBEvent(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    region = Column(String)
    location = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    event_date = Column(DateTime)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

# Создаем таблицы
Base.metadata.create_all(bind=engine)

# Функция для получения данных из API
def fetch_ria_data():
    api_url = "https://cdndc.img.ria.ru/dc/kay-n/2022/SOP-content/data/points/data-24.04.2025.json?v=1196"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "Referer": "https://ria.ru/20220622/spetsoperatsiya-1795199102.html",
    }

    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при запросе к API: {str(e)}")
        raise HTTPException(status_code=500, detail="Ошибка при получении данных")

# Функция для сохранения в БД
def save_to_db(events):
    db = SessionLocal()
    try:
        for event in events:
            db_event = DBEvent(
                region=event['region'],
                location=event['location'],
                latitude=event['latitude'],
                longitude=event['longitude'],
                event_date=datetime.strptime(event['event_date'], "%Y-%m-%d") if event['event_date'] else None,
                description=event['description']
            )
            db.add(db_event)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка при сохранении в БД: {str(e)}")
        raise HTTPException(status_code=500, detail="Ошибка при сохранении данных")
    finally:
        db.close()

# Эндпоинт для загрузки и сохранения данных
@app.post("/load-events/")
async def load_events():
    try:
        # Получаем данные
        raw_data = fetch_ria_data()
        
        # Обрабатываем данные
        events = []
        for item in raw_data:
            # Извлекаем дату из URL
            date_from_url = None
            if 'link' in item:
                try:
                    date_str = item['link'].split('/')[3]
                    date_from_url = datetime.strptime(date_str, "%Y%m%d").strftime("%Y-%m-%d")
                except (IndexError, ValueError):
                    pass
            
            events.append({
                'region': item.get('area', 'Не указано'),
                'location': item.get('fullName', 'Не указано'),
                'latitude': item.get('lat'),
                'longitude': item.get('lng'),
                'event_date': date_from_url,
                'description': item.get('text', '')[:500] + '...'
            })
        
        # Сохраняем в БД
        save_to_db(events)
        
        return {"message": f"Успешно сохранено {len(events)} событий"}
    
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Эндпоинт для получения событий
@app.get("/events/", response_model=list[Event])
async def get_events(limit: int = 100):
    db = SessionLocal()
    try:
        events = db.query(DBEvent).order_by(DBEvent.event_date.desc()).limit(limit).all()
        return events
    finally:
        db.close()

# Эндпоинт для поиска по региону
@app.get("/events/by-region/", response_model=list[Event])
async def get_events_by_region(region: str):
    db = SessionLocal()
    try:
        events = db.query(DBEvent).filter(DBEvent.region.ilike(f"%{region}%")).all()
        return events
    finally:
        db.close()