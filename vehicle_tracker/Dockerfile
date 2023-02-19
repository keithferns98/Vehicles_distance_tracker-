FROM python:3.9
ENV PYTHONDONTWRITEBYTECODE 1
COPY requirements.txt /project/
WORKDIR /project
RUN pip install -r requirements.txt
COPY . /project/