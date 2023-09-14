FROM ubuntu:latest

# Installa le dipendenze richieste
RUN apt-get update && apt-get -y install python3 python3-pip

# Crea una directory all'interno del contenitore
RUN mkdir /app

# Copia i tuoi script nella directory del contenitore
COPY server.py /app
COPY catch_temperature.py /app
COPY send_data.py /app

# Imposta la directory di lavoro all'interno del contenitore
WORKDIR /app

# Installa le dipendenze necessarie
COPY requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt

# Avvia il contenitore e avvia il comando bash
CMD ["/bin/bash"]