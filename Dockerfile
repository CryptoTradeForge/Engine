FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    wget \
    tar \
    gcc \
    make

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY ./bash/install_talib.sh /app/
RUN bash install_talib.sh

CMD ["bash"]