# Specify docker image
# Ansel Lim
FROM continuumio/miniconda3

ADD . /application
WORKDIR /application

RUN conda install numpy pandas geopandas flask
RUN pip install sklearn python-dotenv

ENTRYPOINT ["python", "run.py"]