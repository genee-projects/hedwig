#!/usr/bin/env python
# -*- coding: utf-8 -*-

import dns.resolver
import smtplib
import email
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
            job = beanstalk.reserve()
            job.delete()

            mail_data = json.loads(job.body)

            mail_to = mail_data['to']
            # mail_from = email['from']
            mail_from = config.get('mail_from', 'sender@robot.genee.cn');
            mail_message = email.message_from_string(mail_data['data'])

            logger.info('{from} => {to}: {subject}'.format(to=json.dumps(mail_to), 
                            from=mail_from, subject=mail_message['subject']))
            logger.debug('============\n{d}\n============'.format(d=mail_message.as_string()))

            # 遍历收件人
            for r in mail_to:

                # 进行遍历, 获取到所有的.
                domain = r.split('@')[-1]

                # 获取 MX 记录, 并且存储
                answers = dns.resolver.query(domain, 'MX')
                mx_domain = str(answers[0].exchange)

                logger.debug('MX({rcptto}): {mx_domain}'.format(
                    rcptto=r,
                    mx_domain=mx_domain
                ))

                try:
                    mta = smtplib.SMTP(host=mx_domain, timeout=20)
                    if debug:
                        mta.set_debuglevel(1)
                    mta.sendmail(from_addr=mail_from, to_addrs=mail_to, msg=mail_message.as_string())
                except smtplib.SMTPException as e:
                    logger.warning(
                        'SMTP Error: from: {f}, to: {t}, subject: {s}, reason: {r}'.format(
                            f=mail_from,
                            t=json.dumps(mail_to),
                            s=mail_message['subject']
                            r=str(e)
                        )
                    )
                    logger.debug('============\n{d}\n============'.format(d=mail_message.as_string()))
                except Exception as err:
                    logger.warning('System Error: {err}'.format(err=str(err)))
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