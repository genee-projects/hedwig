# -*- coding: utf-8 -*-
import os
import sys
import getopt
import email

import yaml
import logging
import json

from tornado import gen
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler
from tornado.queues import Queue

from . import worker

__version__ = '0.1.9'

class MainHandler(RequestHandler):

    client = None
    dns = {}

    def brief_mail(self, msg):
        return msg.as_string()

    # 进行 auth 验证
    def initialize(self):

        secret = self.get_argument('secret', None)
        if secret is None:
            secret = self.get_argument('key', None)
        fqdn = self.get_argument('fqdn', None)

        if fqdn in app.clients and app.clients.get(fqdn, None) == secret:
            self.client = fqdn
        else:
            self.client = None

    # 处理请求
    @gen.coroutine
    def post(self):

        if self.client:

            client = self.client
            remote_ip = self.request.headers.get('X-Real-Ip') or self.request.remote_ip

            mail = json.loads(self.get_argument('email'))
            sender = mail['from']
            recipients = mail['to']

            if len(recipients) == 0:
                self.send_error(status_code=406)
                logger.error('Invalid Message!')
                return

            self.finish()

            msg = email.message_from_string(mail['data'])

            # override from
            sender = config.get('mail_from', 'Genee Sender <sender@robot.genee.cn>')

            yield msg_queue.put([client, remote_ip, sender, recipients, msg])

        else:
            self.send_error(status_code=401)

@gen.coroutine
def message_consumer():
    w = worker.Worker()
    while True:
        msg = yield msg_queue.get()
        try:
            yield w.put(msg)
        finally:
            msg_queue.task_done()

def main():

    global config, logger, msg_queue, app

    logger = logging.getLogger('hedwig.nest')
    msg_queue = Queue(maxsize=2)
    app = Application([
        (r"/", MainHandler),
    ])
    config = {}

    try:
        opts, _ = getopt.gnu_getopt(sys.argv[1:], "vc:", ["version", "config"])
    except getopt.GetoptError as _:
        print("Usage: hedwig -c config")
        sys.exit(2)

    configFile = './nest.conf.yml'
    for opt, arg in opts:
        if opt == '-v':
            print(__version__)
            sys.exit()
        elif opt == '-c' or opt == '--config':
            configFile = arg
            break

    with open(configFile, 'r') as f:
        config = yaml.safe_load(f)

    # 设定 Logging
    logging.basicConfig(format='[%(levelname)s] %(message)s')
    if config.get('debug', False):
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    app.clients = config.get('clients', {})
    listen_config = config.get('listen', { 'host': '0.0.0.0', 'port': 80 })
    app.listen(port=listen_config['port'], address=listen_config['host'])

    logger.info('Hedwig Nest is on {host}:{port}...'.format(
        host=listen_config['host'], port=listen_config['port']))

    IOLoop.current().spawn_callback(message_consumer)
    IOLoop.current().start()

if __name__ == '__main__':
    main()