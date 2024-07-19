# -*- coding: utf-8 -*-
import sys
import getopt

import email
import email.header

import asyncio
from aiosmtpd.controller import Controller
import requests
import yaml
import json
import logging
from functools import reduce

__version__ = '0.1.5'

class OwlHandler:
    def decode_header(self, s):
        return reduce(lambda _,x: x[0], email.header.decode_header(s), '')

    async def handle_DATA(self, server, session, envelope):
        mailfrom = envelope.mail_from
        rcpttos = envelope.rcpt_tos
        data = envelope.content

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
            return '250 OK'

        except requests.exceptions.RequestException as err:
            messsage = 'Error: {nest}: {reason}'.format(
                    nest=nest,
                    reason=err
                )
            logger.error(messsage)
            return '500 ' + messsage


def main():

    global config, logger

    logger = logging.getLogger('hedwig.owl')

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

    config = {}
    with open(configFile, 'r') as f:
        config = yaml.safe_load(f)

    # 设定 Logging
    logging.basicConfig(format='[%(levelname)s] %(message)s')
    if config.get('debug', False):
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    listen_config = config.get('listen', { 'host': '0.0.0.0', 'port': 25 })
    handler = OwlHandler()
    controller = Controller(handler, hostname=listen_config['host'], port=listen_config['port'])
    controller.start()
    logger.info('Hedwig Owl is sitting on {host}:{port}...'.format(
        host=listen_config['host'], port=listen_config['port']))

if __name__ == "__main__":
    main()
