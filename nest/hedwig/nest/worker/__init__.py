#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function

import email
import email.header

import dns.resolver
import logging
import smtplib

from tornado import gen

logger = logging.getLogger('hedwig.nest.worker')

class Worker:

    def brief_mail(self, msg):
        return msg.as_string()

    def decode_header(self, s):
        return reduce(lambda _,x: x[0], email.header.decode_header(s), '')

    @gen.coroutine
    def put(self, data):

        sender, recipients, msg = data

        subject = self.decode_header(msg['subject'])

        for recipient in recipients:
            logger.debug('[SENDING] {sender} => {recipient}: "{subject}"'.format(
                sender=sender, recipient=recipient, subject=subject))

            domain = recipient.split('@')[-1]
            server = str(dns.resolver.query(domain, 'MX')[0].exchange)
            
            logger.debug('MX({recipient}) = {server}'.format(
                recipient=recipient,
                server=server
            ))

            try:
                mta = smtplib.SMTP(host=server, timeout=20)
                mta.sendmail(from_addr=sender, to_addrs=recipient, msg=msg.as_string())

                logger.info('[SENT] {sender} => {recipient}: "{subject}"'.format(
                    sender=sender,
                    recipient=recipient,
                    subject=subject
                ))
            except smtplib.SMTPException as err:
                logger.warning(
                    '[FAIL] SMTP Error: {sender} => {recipient}: "{subject}"\nreason: {reason}'.format(
                        sender=sender,
                        recipient=recipient,
                        subject=subject,
                        reason=str(err)
                    )
                )
                logger.debug('============\n{mail}\n============'.format(mail=self.brief_mail(msg)))
            except Exception as err:
                logger.warning('[FAIL] System Error: {err}'.format(err=str(err)))
            finally:
                mta.quit()

