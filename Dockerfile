# 1.a Imagen base ligera con Python 3.12
FROM python:3.12-slim

WORKDIR /app

# 1.b y 1.c Copiar dependencias e instalarlas (primero, para aprovechar la caché)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 1.d Copiar el código fuente
COPY . .

# 1.e Crear un usuario sin privilegios y darle permisos sobre el código
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# 1.f Comando de inicio
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]