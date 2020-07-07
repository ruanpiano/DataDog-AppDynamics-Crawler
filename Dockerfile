ARG name=defaultValue
FROM python:alpine
WORKDIR /

ADD main.py /
ADD install.sh /
ADD env.sh /
ADD start.sh /

RUN sh install.sh

ENTRYPOINT ["sh", "/start.sh"]
