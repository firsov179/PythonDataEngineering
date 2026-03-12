# Energy Dashboard

Мини-дашборд для анализа потребления энергии в России.
Backend: FastAPI | Frontend: Streamlit

## Структура проекта


task_04_service/
├── backend/
│ ├── main.py # FastAPI-приложение
│ └── data.csv # Данные
├── frontend/
│ └── app.py # Streamlit-приложение
├── requirements.txt
└── README.md

## Инструкция по запуску

### 1. Клонируйте репозиторий и перейдите в папку

```bash
git clone <ваш-репозиторий>
cd task_04_service
```

### 2. Создайте и активируйте виртуальное окружение

```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

### 3. Установите зависимости
```
pip install -r requirements.txt
```

### 4. Запустите Backend (FastAPI)
```
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend будет доступен по адресу: http://localhost:8000
Swagger документация: http://localhost:8000/docs

### 5. Запустите Frontend (Streamlit) во втором терминале
```
cd frontend
streamlit run app.py
```

Frontend будет доступен по адресу: http://localhost:8501



