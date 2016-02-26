#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncore, smtpd, requests, yaml


class GServer(smtpd.SMTPServer):
    '''
    继承自smtpd.SMTPServer
    用于把邮件发送请求按照 POST 请求发送到 robots.smtp.genee.cn
    '''

    # 收到邮件发送请求后, 进行邮件发送
    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):

        config = yaml.load('config.yml')

        data = {
            'key': config['key'],
            'fqdn': config['fqdn'],
            'mailfrom': mailfrom,
            'rcpttos': rcpttos,
            'data': data
        }

        requests.post(
            config.get('url', 'robots.smtp.genee.cn'),
            data=data,
            timeout=config.get('timeout', 5)
        )


def main():

    _ = GServer(('0.0.0.0', 25), None)

    try:
        asyncore.loop()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
