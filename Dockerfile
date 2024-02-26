FROM python:3.9

WORKDIR /src

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY ./app app

#CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]