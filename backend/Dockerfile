FROM python:3.11-slim

# Imposta la working directory
WORKDIR /app

# Installa dipendenze di sistema se necessarie
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements e installa le dipendenze
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia il codice backend
COPY . .

# Espone la porta per FastAPI
EXPOSE 8000

# Comando di avvio per FastAPI con reload per development
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]