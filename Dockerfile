FROM alpine:latest

RUN apk update && \
	apk add python3 && \
	rm -rf /var/cache/apk/*

COPY src/* /usr/app/

RUN pip3 install -r /usr/app/requirements.txt

PORT 25

ENTRYPOINT ['/usr/bin/python3', '/usr/app/deliveryman.py']
