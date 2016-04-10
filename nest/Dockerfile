FROM alpine:3.3

ADD . /app
RUN apk add --update py-setuptools && rm -rf /var/cache/apk && cd /app && python setup.py install

VOLUME ["/etc/hedwig"]
EXPOSE 80

CMD ["/usr/bin/hedwig-nest", "-c", "/etc/hedwig/nest.conf.yml"]