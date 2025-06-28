FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["bash", "-c", "scripts/setup_env.sh && streamlit run dashboard/app.py"]
chore: add Dockerfile
