FROM python:3.8.10-slim-buster
WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get install -y git
RUN pip install --no-cache-dir -r requirements.txt
RUN git clone https://github.com/mandarijn4/TINLABML_22-23.git
COPY . .
CMD [ "python3", "./agent/agent.py", "--host", "192.168.56.20"]