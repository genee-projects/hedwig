#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.ioloop
import tornado.web

import yaml
import logging

from pystalkd.Beanstalkd import Connection

logger = logging.getLogger('postoffice')


class MainHandler(tornado.web.RequestHandler):

    authorized = False
    dns = {}

    # 进行 auth 验证
    def initialize(self):

        key = self.get_argument('key', None)
        fqdn = self.get_argument('fqdn', None)

        if fqdn in app.kv and app.kv.get(fqdn, None) == key:
            self.authorized = True
        else:
            self.authorized = False

    # 处理请求
    def post(self):

        if self.authorized:
            # 直接发送

            self.finish()

            email_content = self.get_argument('email')

            if debug:
                logger.debug(email_content)

            beanstalk.put(email_content)

        else:
            self.send_error(status_code=401)


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

if __name__ == "__main__":
    app = make_app()

    with open('postoffice.config.yml', 'r') as f:
        config = yaml.load(f)
        app.kv = config.get('clients', {})

    app.listen(80)

    beanstalk = Connection(config.get('beanstalkd_host', 'localhost'), config.get('beanstalkd_port', 11300))

    # 设定 Logging
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')

    fh = logging.FileHandler('postoffice.log')
    fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    logger.addHandler(fh)

    debug = True if config.get('debug', False) else False

    if debug:
        logger.setLevel(logging.DEBUG)
        logger.debug('Running Debug Mode')
    else:
        logger.setLevel(logging.INFO)

    logger.info('Postoffice is running !')

    tornado.ioloop.IOLoop.current().start()