FROM python:3.10-bullseye

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc-10 \
    g++-10 \
    ffmpeg \
    libsm6 \
    poppler-utils \
 && apt-get clean

ENV CC=gcc-10
ENV CXX=g++-10

# humlib
RUN git clone https://github.com/humdrum-tools/humlib && \
    cd humlib && \
    make 

# humextra
RUN git clone https://github.com/craigsapp/humextra && \
    cd humextra && \
    make && \
    make pae2kern

COPY requirements.txt .
RUN pip install -r requirements.txt