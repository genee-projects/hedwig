#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncore, smtpd


class GServer(smtpd.SMTPServer):

    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        pass


def main():

    _ = GServer(('0.0.0.0', 25), None)

    try:
        asyncore.loop()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
