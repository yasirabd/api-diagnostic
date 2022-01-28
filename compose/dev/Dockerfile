FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

WORKDIR /usr/src/app/src

COPY ./requirements/dev.txt ./

RUN pip install --upgrade pip
RUN python3 -m ensurepip
RUN pip install -r dev.txt

# set environment varibles
# prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
# prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1

ENV PYTHONPATH "${PYTHONPATH}:/usr/src/app/src"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]