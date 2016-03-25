#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import yaml
import json

from pystalkd.Beanstalkd import Connection

from threading import Thread


class Worker(Thread):
    """
    进行 beanstalkd 内容获取后处理使用 Worker
    """

    def run(self):

        beanstalk = Connection(
            config.get('beanstalkd_host', 'localhost'),
            config.get('beanstalkd_port', 11300)
        )

        beanstalk.watch('trash')

        while True:
            job = beanstalk.reserve()
            job.delete()

            logger.info(job.body)

            email = json.loads(job.body)

            mailto = email['to']
            mailfrom = email['from']
            maildata = email['data']

            logger.debug(
                'rcpttos: {r}, mailfrom: {f}, data: {d}'.format(
                    r=json.dumps(mailto),
                    f=mailfrom,
                    d=maildata
                )
            )

logger = logging.getLogger('trash_worker')

if __name__ == "__main__":

    with open('config.yml', 'r') as f:
        config = yaml.load(f)

    # 设定 Logging
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')

    fh = logging.FileHandler('trash.log')
    fh.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'))

    logger.addHandler(fh)

    debug = True if config.get('debug', False) else False

    if debug:
        logger.setLevel(logging.DEBUG)
        logger.debug('Running Debug Mode')
    else:
        logger.setLevel(logging.INFO)

    for i in range(config.get('workers', 1)):
        name = "Thread {id}".format(id=i)
        logger.info("{thread} is running".format(thread=name))
        worker = Worker()
        worker.start()
