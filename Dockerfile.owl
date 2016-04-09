FROM alpine:3.3

RUN apk add --update py-pip && pip install hedwig-owl && rm -rf /var/cache/apk && rm -rf /root/.cache

VOLUME ["/etc/hedwig"]
EXPOSE 25

CMD ["/usr/bin/hedwig-owl", "-c", "/etc/hedwig/owl.conf.yml"]