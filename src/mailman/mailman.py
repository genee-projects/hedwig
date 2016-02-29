#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncore
import smtpd
import requests
import yaml
import json
import sys
import logging

logger = logging.getLogger('Mailman')


class Mailman(smtpd.SMTPServer):
    """
    继承自smtpd.SMTPServer
    用于把邮件发送请求按照 POST 请求发送到 robots.smtp.genee.cn
    """

    def __init__(*args, **kwargs):

        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')

        if 'debug' in kwargs:
            logger.setLevel(logging.DEBUG)
            del kwargs['debug']
            logger.debug('Running Debug Mode')
        else:
            logger.setLevel(logging.INFO)

        logger.info('Running Mailman on port 25')

        smtpd.SMTPServer.__init__(*args, **kwargs)

    # 收到邮件发送请求后, 进行邮件发送
    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):

        with open('config.yml') as f:
            config = yaml.load(f)

        data = {
            'key': config['key'],
            'fqdn': config['fqdn'],
            'mailfrom': mailfrom,
            'rcpttos': rcpttos,
            'data': data
        }

        logger.debug('mailfrom: {mailfrom}, rcpttos: {rcpttos}, data: {data}'.format(
            mailfrom=mailfrom,
            rcpttos=json.dumps(rcpttos),
            data=json.dumps(data)
        ))

        requests.post(
            config.get('url', 'http://robots.smtp.genee.cn/'),
            data=json.dumps(data),
            timeout=config.get('timeout', 5)
        )

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
