FROM alpine:latest

RUN apk update && \
	apk add python3 && \
	rm -rf /var/cache/apk/*

COPY mailman.py /usr/app/

EXPOSE 25

ENTRYPOINT ["/usr/bin/python3", "/usr/app/mailman.py"]
