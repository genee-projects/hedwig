#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.ioloop
import tornado.web

import yaml
import dns.resolver
import smtplib
import json
import logging

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

            email = json.loads(self.get_argument('email'))

            rcpttos = email['rcpttos']
            mailfrom = email['mailfrom']
            data = email['data']

            logger.debug('rcpttos: {rcpttos}, mailfrom: {mailfrom}, data: {data}'.format(
                rcpttos=json.dumps(rcpttos),
                mailfrom=mailfrom,
                data=data
            ))

            # 遍历收件人
            for r in rcpttos:

                # 进行遍历, 获取到所有的.
                domain = r.split('@')[-1]

                if domain not in self.dns:
                    # 获取 MX 记录, 并且存储
                    answers = dns.resolver.query(domain, 'MX')
                    mx_domain = str(answers[0].exchange)

                    self.dns[domain] = mx_domain

                mx_domain = self.dns.get(domain)

                logger.debug('check mx_domain, {rcptto} -> {mx_domain}'.format(
                    rcptto=r,
                    mx_domain=mx_domain
                ))

                try:
                    mta = smtplib.SMTP(mx_domain)

                    if debug:
                        mta.set_debuglevel(1)

                    mta.sendmail(from_addr=mailfrom, to_addrs=rcpttos, msg=data)
                except smtplib.SMTPException as e:
                    logger.warning('邮件发送失败! from: {from_addr}, to: {to_addrs}, data: {data}'.format(
                        from_addr=mailfrom,
                        to_addrs=json.dumps(rcpttos),
                        data=data
                    ))
                    print(e)
                finally:
                    mta.quit()


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

    # 设定 Logging
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')

    fh = logging.FileHandler('postoffice.log')
    fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    logger.addHandler(fh)

    debug = True if app.kv.get('debug', False) else False

    if debug:
        logger.setLevel(logging.DEBUG)
        logger.debug('Running Debug Mode')
    else:
        logger.setLevel(logging.INFO)

    logger.info('Postoffice is running !')

    tornado.ioloop.IOLoop.current().start()