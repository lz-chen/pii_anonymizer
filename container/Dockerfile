FROM ubuntu:20.04

MAINTAINER Lingzhen_Chen

# 1. Define the packages required in our environment.
RUN apt-get -y update && apt-get install -y --no-install-recommends \
         wget \
         python3 \
         python3-pip \
         nginx \
         ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 2. Here we define all python packages we want to include in our environment.
# Pip leaves the install caches populated which uses a significant amount of space.
# These optimizations save a fair amount of space in the image, which reduces start up time.
COPY requirements.txt /opt
RUN pip install -r /opt/requirements.txt && \
        rm -rf /root/.cache

RUN python3 -m spacy download en_core_web_lg
# 3. Set some environment variables. PYTHONUNBUFFERED keeps Python from buffering our standard
# output stream, which means that logs can be delivered to the user quickly. PYTHONDONTWRITEBYTECODE
# keeps Python from writing the .pyc files which are unnecessary in this case. We also update
# PATH so that the train and serve programs are found when the container is invoked.

ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE
ENV PATH="/opt/program:${PATH}"

# 4. Define the folder (sentiment_analysis) where our inference code is located
COPY ./anonymizer /opt/program
WORKDIR /opt/program
RUN chmod +x /opt/program/serve