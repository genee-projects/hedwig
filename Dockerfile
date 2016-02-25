FROM alpine:latest

RUN apk update && \
	apk add python3 && \
	apk add --virtual=build-dependencies wget ca-certificates && \
	wget "https://bootstrap.pypa.io/get-pip.py" -O /dev/stdout | python3 && \
	apk del build-dependencies && \
	rm -rf /var/cache/apk/*

COPY src/* /usr/app/

RUN pip3 install -r /usr/app/requirements.txt

EXPOSE 25

ENTRYPOINT ["/usr/bin/python3", "/usr/app/deliveryman.py"]
