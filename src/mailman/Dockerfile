FROM alpine:latest

RUN apk update && \
	apk add python3 && \
	apk add --virtual=build-dependencies wget ca-certificates && \
	wget "https://bootstrap.pypa.io/get-pip.py" -O /dev/stdout | python3 && \
	apk del build-dependencies && \
	rm -rf /var/cache/apk/*

COPY mailman.py /usr/app/

EXPOSE 25

ENTRYPOINT ["/usr/bin/python3", "/usr/app/mailman.py"]
