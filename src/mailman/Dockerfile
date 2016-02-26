FROM alpine:latest

RUN apk update && \
	apk add python3 && \
	rm -rf /var/cache/apk/*

EXPOSE 25

VOLUME ["/usr/app"]

ENTRYPOINT ["/usr/bin/python3", "/usr/app/mailman.py"]
