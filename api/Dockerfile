FROM python:3.8
WORKDIR /opt
COPY . .

RUN cd /opt/Telethon&&python setup.py install

RUN cd /opt

RUN pip3 install -r requirements.txt

CMD  ["python3", "app.py"]