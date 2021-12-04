# Specify docker image
# Ansel Lim
FROM continuumio/anaconda3:2020.11

ADD . /app
WORKDIR /app

# RUN pip install flask

ENTRYPOINT ["python", "run.py"]