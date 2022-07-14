FROM mashrequae.azurecr.io/python:3.8.0-slim

# set environment variables
ENV PYTHONUNBUFFERED 1

# before copying requirements for cache efficiency
RUN pip install --upgrade pip

RUN apt-get update \
    && apt-get install -y libsasl2-dev python3-numpy python3-scipy python3-pandas gcc g++ \
    && apt-get clean

# seting work directory
WORKDIR /app

# adding requirements file to current directory
COPY requirements.txt .

# install dependecies
RUN pip install -r requirements.txt

# copy code itself from context to image
COPY . .   

# run from working directory, and separate args
CMD ["python", "main.py"]





 