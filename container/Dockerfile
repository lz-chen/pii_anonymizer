FROM ubuntu:20.04

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

# 3. Download necessary language module from spacy
# as of now we support English and Norwegian
RUN python3 -m spacy download en_core_web_md
RUN python3 -m spacy download en_core_web_sm
RUN python3 -m spacy download nb_core_news_md

# 4. Set some environment variables. PYTHONUNBUFFERED keeps Python from buffering our standard
# output stream, which means that logs can be delivered to the user quickly. PYTHONDONTWRITEBYTECODE
# keeps Python from writing the .pyc files which are unnecessary in this case. We also update
# PATH so that the train and serve programs are found when the container is invoked.
ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE
ENV PATH="/opt/program:${PATH}"
ENV PYTHONPATH="/opt/program:${PYTHONPATH}"

# 5. Define the folder where our inference code is located
COPY ./anonymizer /opt/program
WORKDIR /opt/program
RUN chmod +x /opt/program/serve