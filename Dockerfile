FROM ubuntu:22.04

ENV TZ=Asia/Tokyo
RUN apt update
RUN DEBIAN_FRONTEND=noninteractive apt -y install \
    tzdata \
    fonts-ipaexfont \
    libgl1-mesa-dev \
    libglib2.0-0 \
    python3-pip \
    wget

RUN pip3 install \
    numpy==1.26.3 \
    opencv-python==4.9.0.80 \
    pandas==2.1.4 \
    matplotlib==3.8.3 \
    japanize-matplotlib==1.1.3 \
    seaborn==0.13.2 \
    streamlit==1.29.0 \
    mediapipe==0.10.9 \
    av==10.0.0

WORKDIR /home/streamlit
RUN wget -q https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task
COPY src /home/streamlit
