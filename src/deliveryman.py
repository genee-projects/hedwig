#!/usr/bin/env python
# -*- coding: utf-8 -*-

from secure_smtpd import SMTPServer

import dns.resolver, asyncore, smtplib


# 登录验证
class LoginValidator(object):

    # 验证
    def validate(self, username, password):

        print(username)
        print(password)
        return True

        if username == 'foo' and password == 'bar':
            return True

        return False


class SSLSMTPServer(SMTPServer):

    config = []

    dns = {}

    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
          # 直接发送

        # 单独发送给 @geneegroup.com 的邮件, 特殊处理
        if (len(rcpttos) == 1) and ('@geneegroup.com' in rcpttos[0]):
            pass
        else:

            # 可直接递送, 不需要 MTA
            for r in rcpttos:
                # 进行遍历, 获取到所有的.
                domain = r.split('@')[-1]

                if not domain in self.dns:
                    # 获取 MX 记录, 并且存储
                    answers = dns.resolver.query(domain, 'MX')
                    mx_domain = str(answers[0].exchange)
                    self.dns[domain] = mx_domain

                mx_domain = self.dns.get(domain)

                mta = smtplib.SMTP(mx_domain)
                mta.sendmail(from_addr=mailfrom, to_addrs=rcpttos, msg=data)
                mta.quit()


def main():

    try:
        server = SMTPServer(
            ('0.0.0.0', 25),
            ('0.0.0.0', 465),
            require_authentication=True,
            ssl=True,
            certfile='examples/server.crt',
            keyfile='examples/server.key',
            credential_validator=LoginValidator()
        )

        server.run()

    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
