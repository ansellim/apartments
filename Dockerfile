# Specify docker image
# Ansel Lim
FROM continuumio/miniconda3

ADD . /application
WORKDIR /application

RUN conda install flask

ENTRYPOINT ["python", "run.py"]