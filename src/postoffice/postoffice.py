#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Flask, request

app = Flask(__name__)


@app.route('/post', methods=['POST'])
def post():
    print(request)


if __name__ == '__main__':
    app.run()
