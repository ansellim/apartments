# Specify docker image
# Ansel Lim
FROM continuumio/miniconda3

ADD . /application
WORKDIR /application

COPY environment.yml .
RUN conda env create -f environment.yml
SHELL ["conda", "run", "-n", "apartments-project", "/bin/bash", "-c"]

RUN echo "Make sure flask is installed"
RUN python -c "import flask"

ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "apartments-project", "python", "run.py"]