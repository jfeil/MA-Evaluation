FROM python:3.11-bookworm
LABEL authors="jfeil"

WORKDIR /workdir

COPY requirements.txt /workdir
RUN pip install -r requirements.txt

COPY main.py /workdir
COPY src /workdir/src

EXPOSE 8080

RUN apt install libpq-dev
RUN pip install -r requirements.txt

ENTRYPOINT ["gunicorn", "main:server", "-b", ":8080"]