FROM python:3.6
WORKDIR /app
ADD ./requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt
ADD . /app
ENTRYPOINT [ "python3","api.py" ]