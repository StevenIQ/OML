FROM python:3.8-slim

# Indispensable pour LightGBM
RUN apt update
RUN apt install libgomp1 -y

# Mise à jour de pip3
RUN pip install --upgrade pip
RUN python3 --version

RUN mkdir /app

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY app/app.py /app/app.py
COPY app/src/ /app/src/
COPY app/conf/key.json /app/conf/key.json

# On ouvre et expose le port 80
EXPOSE 80

# Lancement de l'API
# Attention : ne pas lancer en daemon !
CMD ["flask", "run", "--host", "0.0.0.0", "--port", "80"]
# CMD ["gunicorn", "app:app", "-b", "0.0.0.0:80", "-w", "4"]