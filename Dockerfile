##
## Python Dockerfile
##
## Pull base image.
FROM python:2-alpine
MAINTAINER Ryan Criss "rcriss@cisco.com"
EXPOSE 5000

RUN pip install --no-cache-dir setuptools wheel
RUN pip install --upgrade pip

ADD . /app
WORKDIR /app
RUN pip install --requirement requirements.txt

CMD ["python", "c2k_listener.py"]

