FROM public.ecr.aws/lambda/python:3.8

COPY requirements/prod.txt ${LAMBDA_TASK_ROOT}

RUN pip install --upgrade pip
RUN python3 -m ensurepip
RUN pip install -r prod.txt

# set environment varibles
# prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
# prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1

ADD src ${LAMBDA_TASK_ROOT}

CMD [ "main.handler" ]