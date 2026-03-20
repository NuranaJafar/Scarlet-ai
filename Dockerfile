FROM python:3.11-slim

WORKDIR /app

# Önce gereksinimleri yükle (Cache için)
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Tüm projeyi kopyala (backend ve frontend klasörleri dahil)
COPY . .

# Backend klasörüne geçerek çalıştır
WORKDIR /app/backend

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]