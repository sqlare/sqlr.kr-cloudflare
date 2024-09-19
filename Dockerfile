FROM python:alpine3.19

COPY . .

RUN pip install -r requirements.txt

CMD ./start.sh

EXPOSE 2001
