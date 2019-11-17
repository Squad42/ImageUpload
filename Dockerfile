FROM python:3.6.8-alpine

LABEL Squad42 project: image for ImageUpload microservice

COPY imageUpload/ /imageUpload
COPY requirements.txt /imageUpload/
WORKDIR /imageUpload/

RUN apk add build-base python-dev py-pip jpeg-dev zlib-dev
ENV LIBRARY_PATH=/lib:/usr/lib
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

EXPOSE 5000

ENV FLASK_APP=server.py
CMD ["python3","-m","flask","run", "--host", "0.0.0.0", "--port", "5000"]

