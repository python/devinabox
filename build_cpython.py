#!/usr/bin/env python
"""Build CPython"""
import multiprocessing
import os
import subprocess
import sys

if sys.platform == 'win32':
    print("See the devguide's Getting Set Up guide for building under Windows")

directory = 'cpython'
cwd = os.getcwd()
os.chdir(directory)
try:
    if os.path.isfile('Makefile'):
        print('Makefile already exists; skipping ./configure')
    else:
        subprocess.check_call(['./configure', '--prefix=/dev/null',
                               '--with-pydebug'])
    make_cmd = ['make', '-s', '-j', str(multiprocessing.cpu_count())]
    subprocess.call(make_cmd)
finally:
    os.chdir(cwd)
