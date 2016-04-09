#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function

import sys
import getopt
import asyncore

import email
import email.header

import smtpd
import requests
import yaml
import json
import logging

__version__ = '0.1.4'

class Owl(smtpd.SMTPServer):
    """
    继承自smtpd.SMTPServer
    用于把邮件发送请求按照 POST 请求发送到 robot.genee.cn
    """

    def decode_header(self, s):
        return reduce(lambda _,x: x[0], email.header.decode_header(s), '')

    # 收到邮件发送请求后, 进行邮件发送
    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):

        global config, logger

        msg = email.message_from_string(data)

        subject = self.decode_header(msg['subject'])
        logger.debug(
            '{sender} => {recipients}: "{subject}"'.format(
                sender=mailfrom,
                recipients=', '.join(rcpttos),
                subject=subject
            )
        )

        nest = config.get('nest', 'http://robot.genee.cn')

        # 尝试递送邮件到 hedwig.nest
        try:
            r = requests.post(
                nest,
                data={
                    'fqdn': config['fqdn'],
                    'secret': config['secret'],
                    'email': json.dumps({
                        'from': mailfrom,
                        'to': rcpttos,
                        'data': data,
                    })
                },
                timeout=config.get('timeout', 5)
            )

            # 不为 OK, raise exception
            r.raise_for_status()

        except requests.exceptions.RequestException as err:
            logger.error(
                'Error: {nest}: {reason}'.format(
                    nest=nest,
                    reason=str(err)
                )
            )

        return None


def main():

    try:
        opts, _ = getopt.gnu_getopt(sys.argv[1:], "vc:", ["version", "config"])
    except getopt.GetoptError as _:
        print("Usage: hedwig -c config")
        sys.exit(2)

    configFile = './owl.conf.yml'
    for opt, arg in opts:
        if opt == '-v':
            print(__version__)
            sys.exit()
        elif opt == '-c' or opt == '--config':
            configFile = arg
            break

    global config, logger
    with open(configFile, 'r') as f:
        config = yaml.load(f)

    # 设定 Logging
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
    if config.get('debug', False):
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    listen_config = config.get('listen', { 'host': '0.0.0.0', 'port': 25 })
    owl = Owl((listen_config['host'], listen_config['port']), None)
    logger.info('Hedwig Owl is sitting on {host}:{port}...'.format(
        host=listen_config['host'], port=listen_config['port']))
    asyncore.loop()

logger = logging.getLogger('hedwig.owl')
config = {}

if __name__ == '__main__':
    main()
