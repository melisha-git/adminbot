FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

ENV BOT_TOKEN=""

CMD ["python", "-m", "binnotesbot"]