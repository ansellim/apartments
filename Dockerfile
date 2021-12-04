# Specify docker image
# Ansel Lim
FROM continuumio/anaconda3:2021.05
ADD . /code
WORKDIR /code
ENTRYPOINT ["python","run.py"]