FROM python:3.12.3-slim
LABEL authors="Miguel Angel Quintana Sanchez"

# Ajuste de la zona horaria a CDMX
RUN apt-get update && apt-get install -y tzdata && \
    ln -fs /usr/share/zoneinfo/America/Mexico_City /etc/localtime && \
    dpkg-reconfigure --frontend noninteractive tzdata && \
    apt-get clean

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY /src ./src

COPY /front ./front

COPY __init__.py .

COPY meta.npz .

EXPOSE 80:8000

CMD ["python", "__init__.py"]