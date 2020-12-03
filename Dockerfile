FROM python:3.8-slim-buster

USER root
WORKDIR /tmp

# for source
RUN rm /bin/sh && ln -s /bin/bash /bin/sh

# for compile
RUN  apt-get update \
  && apt-get install -y wget \
  && apt-get install -y build-essential \
  && rm -rf /var/lib/apt/lists/*

# for TA-Lib
RUN pip install numpy && \
  wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
  tar -xvzf ta-lib-0.4.0-src.tar.gz && \
  cd ta-lib/ && \
  ./configure --prefix=/usr && \
  make && \
  make install
RUN rm -R ta-lib ta-lib-0.4.0-src.tar.gz

# set the working directory in the container
WORKDIR /code
# copy the dependencies file to the working directory
COPY requirements.txt .
# install dependencies
RUN pip3 install -r requirements.txt
# copy the content of the local src directory to the working directory
COPY src/ .
# command to run on container start
CMD [ "python", "./core/main.py" ]
