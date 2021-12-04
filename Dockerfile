# Specify docker image
# Ansel Lim
FROM continuumio/anaconda3:2021.05

ADD . /code
WORKDIR /code

COPY environment.yml
RUN conda env create -f environment.yml
SHELL ["conda", "run", "-n", "apartments-project", "/bin/bash", "-c"]

RUN python -c "import flask"

ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "apartments-project", "python", "run.py"]