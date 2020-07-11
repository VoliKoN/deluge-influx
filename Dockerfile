FROM python:3-alpine

COPY requirements.txt /

RUN pip install -r requirements.txt

COPY deluge-influx.py /

WORKDIR /
CMD ["/usr/local/bin/python", "deluge-influx.py"]
