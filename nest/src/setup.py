# -*- coding: utf-8 -*-
import codecs
import os
import re
import sys

from setuptools import find_packages, setup

# disable ssl verify since it might failed during docker-build
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

def read(*parts):
    path = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(path, encoding='utf-8') as fobj:
        return fobj.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

nest_requires = [
    'PyYAML',
    'tornado',
    'dnspython',
    'pyIsEmail'
]

setup(
    name='hedwig-nest',
    version=find_version("hedwig/nest", "__init__.py"),
    description='Hedwig Nest for Mail Dispatching',
    url='https://github.com/genee-projects/hedwig',
    author="Jia Huang",
    author_email="iamfat@gmail.com",
    license='MIT',
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
    ],
    keywords='hedwig',
    packages=find_packages(exclude=['tests.*', 'tests']),
    install_requires=nest_requires,
    entry_points={
        'console_scripts': [
            'hedwig-nest=hedwig.nest:main',
        ],
    },
)