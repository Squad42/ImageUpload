FROM python:3.6.8-alpine

MAINTAINER Squad42 "mb2551@student.uni-lj.si"

LABEL image for ImageUpload microservice

WORKDIR /app

COPY requirements.txt /app

RUN pip3 install -r requirements.txt

COPY imageUpload/ /app

ENTRYPOINT ["python"]

EXPOSE 5000

CMD ["server.py"]

