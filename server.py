from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

import time
import pandas as pd
from selenium.webdriver.chrome.service import Service

# Укажите абсолютный путь к chromedriver
driver_path = '/home/pc1243/Рабочий стол/PROJECT/SERVER/chromedriver'

# Настройка сервиса для ChromeDriver
service = Service(driver_path)
driver = webdriver.Chrome(service=service)


driver.get("https://ria.ru/20220622/spetsoperatsiya-1795199102.html")

# Ждем загрузки карты
time.sleep(5)  # Может потребоваться увеличить время

try:
    # Находим все элементы-кружочки на карте
    # (селектор нужно уточнить через инструменты разработчика)
    circles = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#Ellipse\ 496_3"))  # Замените на актуальный селектор
    )
    
    events_data = []
    
    for i, circle in enumerate(circles):
        try:
            # Кликаем на кружок
            circle.click()
            
            # Ждем появления всплывающего окна
            popup = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "#Ellipse\ 496_3"))  # Замените на актуальный селектор
            )
            
            # Извлекаем информацию из всплывающего окна
            title = popup.find_element(By.CSS_SELECTOR, ".title-class").text  # Замените селекторы
            date = popup.find_element(By.CSS_SELECTOR, ".date-class").text
            description = popup.find_element(By.CSS_SELECTOR, ".desc-class").text
            
            # Добавляем данные в список
            events_data.append({
                'id': i,
                'title': title,
                'date': date,
                'description': description
            })
            
            # Закрываем всплывающее окно (если есть кнопка закрытия)
            close_button = popup.find_element(By.CSS_SELECTOR, ".close-class")
            close_button.click()
            
            # Небольшая пауза между кликами
            time.sleep(1)
            
        except (NoSuchElementException, TimeoutException) as e:
            print(f"Ошибка при обработке кружка {i}: {str(e)}")
            continue
    
    # Сохраняем данные в CSV
    df = pd.DataFrame(events_data)
    df.to_csv('events_data.csv', index=False)
    print(f"Сохранено {len(events_data)} событий")
    
finally:
    driver.quit()