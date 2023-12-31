FROM python:3.11.3-slim
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY ./src/ /app/
CMD ["python3", "-u", "main.py"]