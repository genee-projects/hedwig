#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
  Usage:
     key_generator.py fqdn
"""

import sys

import string
import random

from string import Template

s = """
请复制如下内容到 mailman 的 config.yml 中:

---
fqdn: $fqdn
key: $key
...

请复制如下内容到 postoffice 的 config.yml 中:

$fqdn: $key
"""

if len(sys.argv) == 1:
    print(__doc__)
    sys.exit()

fqdn = sys.argv[1]
key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))


d = dict(
    fqdn=fqdn,
    key=key
)

print(Template(s).substitute(d))