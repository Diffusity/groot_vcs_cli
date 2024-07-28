#!/usr/bin/env python3

from setuptools import setup

setup (name = 'groot',
       version = '1.0',
       packages = ['groot'],
       entry_points = {
           'console_scripts' : [
               'groot = groot.cli:main'
           ]
       })
