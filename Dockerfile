FROM python:3.7-slim

WORKDIR /m365MessageCenter

COPY requirements.txt /m365MessageCenter/
RUN pip install -r /m365MessageCenter/requirements.txt
COPY . /m365MessageCenter/

CMD python3 -u /m365MessageCenter/m365bot/main.py
