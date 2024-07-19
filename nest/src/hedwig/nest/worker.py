#!/usr/bin/env python
# -*- coding: utf-8 -*-


import email
import email.header

import dns.resolver
import logging
import smtplib

from tornado import gen
from pyisemail import is_email
from functools import reduce

logger = logging.getLogger('hedwig.nest')


class Worker:

    def brief_mail(self, msg):
        return msg.as_string()

    def decode_header(self, s):
        try:
            return reduce(lambda _,x: x[0].decode(x[1], 'ignore') if type(x[0])==bytes and x[1] is not None else x[0], email.header.decode_header(s), '')
        except Exception:
            return s

    @gen.coroutine
    def put(self, data):

        client, ip, sender, recipients, msg = data

        subject = self.decode_header(msg['subject'])

        for recipient in recipients:
            if not is_email(recipient):
                logger.error('[{client}:{ip}] {sender} => {recipient}: "{subject}"'.format(
                    client=client, ip=ip, sender=sender, recipient=recipient, subject=subject))
                continue

            logger.info('[{client}:{ip}] {sender} => {recipient}: "{subject}"'.format(
                client=client, ip=ip, sender=sender, recipient=recipient, subject=subject))

            try:
                domain = recipient.split('@')[-1]
                answer = dns.resolver.query(domain, 'MX')
                server = answer[0].exchange.to_text(omit_final_dot=True)
                logger.debug('[{client}:{ip}] MX({recipient}) = {server}'.format(
                    client=client, ip=ip,
                    recipient=recipient,
                    server=server))
            except Exception as err:
                logger.error('[{client}:{ip}] Query MX({recipient}): {err}'.format(
                    client=client, ip=ip,
                    recipient=recipient, err=err))
                continue
            config = {}
            try:
                mta = smtplib.SMTP(host=server, timeout=20)
                if 'user' in config and 'password' in config:
                    mta.login(config['user'], config['password'])
                mta.sendmail(from_addr=sender, to_addrs=recipient,
                             msg=msg.as_string())
                mta.quit()
            except smtplib.SMTPException as err:
                logger.error(
                    '[{client}:{ip}] SMTP Error: {sender} => {recipient}: "{subject}"\nreason: {reason}'.format(
                        client=client, ip=ip,
                        sender=sender,
                        recipient=recipient,
                        subject=subject,
                        reason=err
                    )
                )
                logger.debug('============\n{mail}\n============'
                             .format(mail=self.brief_mail(msg)))
            except Exception as err:
                logger.error('[{client}:{ip}] System Error: {err}'.format(
                    client=client, ip=ip, err=err))
