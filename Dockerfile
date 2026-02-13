FROM python:3.13-slim

WORKDIR /app

COPY . .

RUN  pip install -r requirements.txt


COPY . .

EXPOSE 8501

CMD ["streamlit","run","src/main.py", "--server.port=8501", "--server.address=0.0.0.0"]