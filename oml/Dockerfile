FROM python:3.8-slim

RUN apt update
# Nécessaire pour charger le modèle
RUN apt-get install libgomp1 -y

# Mise à jour de pip3
RUN pip install --upgrade pip
RUN python3 --version

RUN mkdir /app

WORKDIR /app

COPY requirements.txt /app/
COPY app.py /app/
COPY src/ /app/src/

RUN pip install --no-cache-dir -r requirements.txt

# On ouvre et expose le port
EXPOSE $PORT

# Lancement de l'API
# Attention : ne pas lancer en daemon !
CMD exec gunicorn -b :$PORT -w 4 app:app
