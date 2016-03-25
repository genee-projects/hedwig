#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json
import logging
import yaml

from pystalkd.Beanstalkd import Connection


# 分发 data 到 worker
def dispatch(data, worker):
    beanstalk.use(worker)
    beanstalk.put(data)


if __name__ == "__main__":

    logger = logging.getLogger('dispatcher')

    with open('dispatcher.config.yml', 'r') as f:
        config = yaml.load(f)

    beanstalk = Connection(
        config.get('beanstalkd_host', 'localhost'),
        config.get('beanstalkd_port', 11300)
    )

    # 设定 Logging
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')

    fh = logging.FileHandler('doorman.log')

    fh.setFormatter(
        logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
    )

    logger.addHandler(fh)

    debug = True if config.get('debug', False) else False

    if debug:
        logger.setLevel(logging.DEBUG)
        logger.debug('Running Debug Mode')
    else:
        logger.setLevel(logging.INFO)

    logger.info('Doorman is running !')

    while True:
        beanstalk.use('work')
        job = beanstalk.reserve()
        job.delete()

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

        if len(mailto) > 1:
            # 如果mailto 比一个人多, 那么直接给 send work
            dispatch(email, 'send')
        else:
            pass
