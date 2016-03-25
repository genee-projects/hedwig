#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json
import logging
import yaml

from pystalkd.Beanstalkd import Connection


# 分发 data 到 worker
def dispatch(data, tube):

    logger.debug('data: {data} push to {tube}'.format(
        tube=tube,
        data=data
    ))

    beanstalk.use(tube)
    beanstalk.put(data)


def first_worker():

    return workers[0]


# 获取下一个 worker
def next_worker(worker):

    index = workers.index(worker)
    return workers[index + 1]


if __name__ == "__main__":

    logger = logging.getLogger('app')

    with open('config.yml', 'r') as f:
        config = yaml.load(f)
        workers = config.get('workers', [])

    beanstalk = Connection(
        config.get('beanstalkd_host', 'localhost'),
        config.get('beanstalkd_port', 11300)
    )

    # 设定 Logging
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')

    fh = logging.FileHandler('dispatcher.log')

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

    logger.info('Dispatcher is running !')

    beanstalk.watch('porch')

    while True:

        job = beanstalk.reserve()
        job.delete()

        email = json.loads(job.body)

        # 邮件相关信息
        mailto = email['to']
        mailfrom = email['from']
        maildata = email['data']

        # 数据相关信息
        worker = email.get('worker', None)
        trash = email.get('trash', False)

        logger.debug(
            'rcpttos: {r}, mailfrom: {f}, data: {d}'.format(
                r=json.dumps(mailto),
                f=mailfrom,
                d=maildata
            )
        )

        data = json.dumps(email)

        if len(mailto) == 1:
            # 如果要丢到垃圾桶里面, 那么, 丢
            if trash:
                dispatch(data, 'trash')
            elif worker is None:
                # 如果 worker 为 None, 那么发给第一个, 其他的发给下一个
                dispatch(data, first_worker())
            else:
                dispatch(data, next_worker(worker))
        else:
            # 如果mailto 比一个人多, 那么直接给 send worker, 让 send worker 进行处理
            dispatch(data, 'send')