FROM postgres:14

ENV POSTGRES_DB=vacancies
ENV POSTGRES_USER=your_user
ENV POSTGRES_PASSWORD=your_password

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
