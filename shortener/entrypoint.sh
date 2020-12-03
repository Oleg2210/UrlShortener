#!/bin/bash
while ! nc -z $SQL_HOST $SQL_PORT; do
  sleep 0.2
done

env | while read -r LINE; do
    IFS="=" read VAR VAL <<< ${LINE}
    sed --in-place "/^${VAR}/d" /etc/security/pam_env.conf || true
    echo "${VAR} DEFAULT=\"${VAL}\"" >> /etc/security/pam_env.conf
done

cron


python3 manage.py makemigrations api
python3 manage.py migrate
python3 manage.py collectstatic --noinput
gunicorn --bind 0.0.0.0:8000 url_shorter.wsgi