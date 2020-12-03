FROM ubuntu:18.04

WORKDIR /app
#RUN pip install --upgrade pip

RUN apt-get update
RUN apt-get install python3 python3-pip python3-dev default-libmysqlclient-dev gcc netcat cron  -y

COPY requirements.txt /app
RUN pip3 install -r requirements.txt

COPY entrypoint.sh /app
COPY cronfile /etc/cron.d/crontab
RUN chmod 644 /etc/cron.d/crontab
RUN crontab /etc/cron.d/crontab

COPY app/ /app
ENTRYPOINT ["/app/entrypoint.sh"]