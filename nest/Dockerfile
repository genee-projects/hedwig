FROM alpine:3

RUN apk add --no-cache py3-setuptools

ADD . /app
RUN cd /app/src && python3 setup.py install && rm -rf /app/src

VOLUME ["/etc/hedwig"]
EXPOSE 80

WORKDIR /app
ENV PATH=/app/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
    NEST_ADDR=80

CMD ["/usr/bin/hedwig-nest", "-c", "/etc/hedwig/nest.conf.yml"]