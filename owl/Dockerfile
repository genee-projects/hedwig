FROM alpine:3.3

ADD . /app
RUN apk add --update py-setuptools && rm -rf /var/cache/apk && cd /app && python setup.py install

VOLUME ["/etc/hedwig"]
EXPOSE 25

CMD ["/usr/bin/hedwig-owl", "-c", "/etc/hedwig/owl.conf.yml"]