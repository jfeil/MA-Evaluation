FROM python:3.11-bookworm
LABEL authors="jfeil"

WORKDIR /workdir

COPY requirements.txt /workdir
RUN apt install libpq-dev
RUN pip install -r requirements.txt

COPY main.py /workdir
COPY src /workdir/src
COPY pages /workdir/pages
COPY assets /workdir/assets

EXPOSE 8080

ENTRYPOINT ["gunicorn", "main:server", "-b", ":8080"]