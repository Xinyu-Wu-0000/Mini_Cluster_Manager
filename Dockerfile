FROM continuumio/miniconda3:23.10.0-1

WORKDIR /usr/src/app

COPY ./requirements.txt .
RUN conda install pip \
    && pip install torch==2.2.0 torchvision==0.17.0 torchaudio==2.2.0 --index-url https://download.pytorch.org/whl/cpu \
    && pip install -r requirements.txt

COPY ./task2.py .
COPY ./task3.py .
