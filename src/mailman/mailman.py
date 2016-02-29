#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncore
import smtpd
import requests
import yaml
import json
import sys
import logging

logger = logging.getLogger('mailman')


class Mailman(smtpd.SMTPServer):
    """
    继承自smtpd.SMTPServer
    用于把邮件发送请求按照 POST 请求发送到 robots.smtp.genee.cn
    """

    config = {}

    def __init__(*args, **kwargs):

        # 设定 Logging
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')

        fh = logging.FileHandler('mailman.log')
        fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        logger.addHandler(fh)

        # 判断是否开启 Debug 默认开启
        if 'debug' in kwargs:
            logger.setLevel(logging.DEBUG)
            del kwargs['debug']
            logger.debug('Running Debug Mode')
        else:
            logger.setLevel(logging.INFO)

        # 提示服务开启
        logger.info('Running Mailman on port 25')

        # 开启服务
        smtpd.SMTPServer.__init__(*args, **kwargs)

        # 加载配置
        with open('config.yml') as f:
            config = yaml.load(f)

        logger.info('config: fqdn {fqdn}, key {key}'.format(
            fqdn=config['fqdn'],
            key=config['key'],
        ))

        Mailman.config = config

    # 收到邮件发送请求后, 进行邮件发送
    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):

        config = self.config

        logger.debug('mailfrom: {mailfrom}, rcpttos: {rcpttos}, data: {data}'.format(
            mailfrom=mailfrom,
            rcpttos=json.dumps(rcpttos),
            data=json.dumps(data)
        ))

        # 尝试递送邮件到 postoffice
        try:
            r = requests.post(
                config.get('url', 'http://robots.smtp.genee.cn/'),
                data={
                    'fqdn': config['fqdn'],
                    'key': config['key'],
                    'email': json.dumps({
                        'mailfrom': mailfrom,
                        'rcpttos': rcpttos,
                        'data': data
                    })
                },
                timeout=config.get('timeout', 5)
            )

            # 不为 OK, raise exception
            if r.status_code != requests.codes.ok:
                raise requests.exceptions.RequestException

        except requests.exceptions.RequestException:
            # http://docs.python-requests.org/zh_CN/latest/user/quickstart.html
            logger.warning('{url} is down!!!'.format(url=config.get('url', 'http://robots.smtp.genee.cn')))

        return None


def main():

    debug = True if '--deubg' in sys.argv or '-d' in sys.argv else False

    mm = Mailman(('0.0.0.0', 25), None, debug=debug)

    try:
        asyncore.loop()
    except KeyboardInterrupt:
        mm.close()

if __name__ == '__main__':
    main()
