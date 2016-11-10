##
## Python Dockerfile
##
## Pull base image.
FROM python:2-alpine
MAINTAINER Ryan Criss "rcriss@cisco.com"
EXPOSE 5000

RUN pip install --no-cache-dir setuptools wheel

ADD . /app
WORKDIR /app
RUN pip install --requirement /app/requirements.txt

CMD ["python", "c2K_listener.py"]

