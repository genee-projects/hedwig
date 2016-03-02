#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request, session, make_response, abort

import yaml
import dns.resolver
import smtplib
import json
import logging
import sys

logger = logging.getLogger('postoffice')

app = Flask(__name__)


# 每次请求都进行验证
@app.before_request
def before_request():

    key = request.form.get('key', None)
    fqdn = request.form.get('fqdn', None)

    if 'fqdn' not in session:
        if fqdn in app.kv and app.kv.get(fqdn, None) == key:
            session['fqdn'] = fqdn


# 增加 Route, 只支持 / 路径传递
@app.route('/', methods=['POST'])
def post():

    # 简单得进行验证
    if session.get('fqdn', False):

        email = json.loads(request.form['email'])

        rcpttos = email['rcpttos']
        mailfrom = email['mailfrom']
        data = email['data']

        logger.debug('rcpttos: {rcpttos}, mailfrom: {mailfrom}, data: {data}'.format(
            rcpttos=json.dumps(rcpttos),
            mailfrom=mailfrom,
            data=data
        ))

        # 遍历收件人
        for r in rcpttos:

            # 进行遍历, 获取到所有的.
            domain = r.split('@')[-1]

            if domain not in app.dns:
                # 获取 MX 记录, 并且存储

                answers = dns.resolver.query(domain, 'MX')
                mx_domain = str(answers[0].exchange)

                app.dns[domain] = mx_domain

            mx_domain = app.dns.get(domain)

            logger.debug('check mx_domain, {rcptto} -> {mx_domain}'.format(
                rcptto=r,
                mx_domain=mx_domain
            ))
            try:
                mta = smtplib.SMTP(mx_domain)
                mta.sendmail(from_addr=mailfrom, to_addrs=rcpttos, msg=data)
            except smtplib.SMTPException:
                logger.warning('邮件发送失败! from: {from_addr}, to: {to_addrs}, data: {data}'.format(
                    from_addr=mailfrom,
                    to_addrs=json.dumps(rcpttos),
                    data=data
                ))
            finally:
                mta.quit()

        response = make_response('', 200)
        return response
    else:
        abort(401)


if __name__ == '__main__':

    try:
        # 初始化设定 app 部分参数
        with app.app_context():
            with open('config.yml', 'r') as f:
                app.kv = yaml.load(f)
    except FileNotFoundError:
        sys.stderr.write('\nError: Unable to find config.yml\n')
        sys.exit(1)

    app.dns = {}

    # 设定 Logging
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')

    fh = logging.FileHandler('postoffice.log')
    fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    logger.addHandler(fh)

    debug = True if '--deubg' in sys.argv or '-d' in sys.argv else False

    if debug:
        logger.setLevel(logging.DEBUG)
        logger.debug('Running Debug Mode')
    else:
        logger.setLevel(logging.INFO)

    logger.info('Postoffice is running !!!')

    app.secret_key = '3*&0_oZyEH'
    app.run(port=80, host='0.0.0.0', debug=debug)