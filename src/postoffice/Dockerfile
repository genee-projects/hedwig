FROM alpine:latest

RUN apk update && \
	apk add python3 && \
	apk add --virtual=build-dependencies wget ca-certificates && \
	wget "https://bootstrap.pypa.io/get-pip.py" -O /dev/stdout | python3 && \
	apk del build-dependencies && \
	rm -rf /var/cache/apk/*

EXPOSE 80

VOLUME ["/usr/app"]

ONBUILD COPY requirements.txt
ONBUILD RUN pip3 install

ENTRYPOINT ["/usr/bin/python3", "/usr/app/postoffice.py"]
