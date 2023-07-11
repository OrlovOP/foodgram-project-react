FROM python:3.9-slim

WORKDIR /app

RUN pip install gunicorn==20.1.0

COPY foodgram/requirements.txt ./

RUN pip3 install -r requirements.txt --no-cache-dir

COPY foodgram/ .

RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]