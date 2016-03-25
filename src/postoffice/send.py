#!/usr/bin/env python
# -*- coding: utf-8 -*-

import dns.resolver
import smtplib
import json
import logging
import yaml

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

        while True:
            beanstalk.use('send')
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

            # 遍历收件人
            for r in mailto:

                # 进行遍历, 获取到所有的.
                domain = r.split('@')[-1]

                # 获取 MX 记录, 并且存储
                answers = dns.resolver.query(domain, 'MX')
                mx_domain = str(answers[0].exchange)

                logger.info('check mx_domain, {rcptto} -> {mx_domain}'.format(
                    rcptto=r,
                    mx_domain=mx_domain
                ))

                try:
                    mta = smtplib.SMTP(mx_domain)

                    if debug:
                        mta.set_debuglevel(1)

                    mta.sendmail(from_addr=mailfrom,
                                 to_addrs=mailto, msg=maildata)
                except smtplib.SMTPException as e:
                    logger.warning(
                        '发送失败! from: {f}, to: {t}, data: {d}'.format(
                            f=mailfrom,
                            t=json.dumps(mailto),
                            d=maildata
                        )
                    )
                    logger.info('失败原因: {r}'.format(r=str(e)))
                finally:
                    mta.quit()


logger = logging.getLogger('worker')

if __name__ == "__main__":

    with open('worker.config.yml', 'r') as f:
        config = yaml.load(f)

    # 设定 Logging
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')

    fh = logging.FileHandler('worker.log')
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
