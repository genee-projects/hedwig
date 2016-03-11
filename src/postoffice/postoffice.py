#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.ioloop
import tornado.web

import yaml
import beanstalkc


class MainHandler(tornado.web.RequestHandler):

    authorized = False

    # 进行 auth 验证
    def initialize(self):

        key = self.get_argument('key', None)
        fqdn = self.get_argument('fqdn', None)

        if fqdn in app.kv and app.kv.get(fqdn, None) == key:
            self.authorized = True
        else:
            self.authorized = True

    # 处理请求
    def get(self):

        if self.authorized:
            # 推送到 Beanstalkd 中
            app.beans.put(self.get_argument('email'))
        else:
            self.send_error(status_code=401)


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(80)

    with open('config.yml', 'r') as f:
        config = yaml.load(f)
        app.kv = config.get('clients', {})

    app.beans = beanstalkc.Connection(host=config.get('beanstalkd_host'), port=config.get('beanstalkd_port'))

    tornado.ioloop.IOLoop.current().start()