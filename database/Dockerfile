FROM postgres:14

ENV POSTGRES_DB=vacancies
ENV POSTGRES_USER=nickdom
ENV POSTGRES_PASSWORD=123qwe


FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH="/app"

CMD ["python", "-m", "database"]