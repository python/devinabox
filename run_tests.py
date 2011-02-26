#!/usr/bin/env python
"""Run CPython's test suite in the most rigorous way possible."""
import multiprocessing
import os
import subprocess
import sys


directory = 'cpython'
cmd = os.path.join(directory, 'python')
# UNIX
if not os.path.isfile(cmd):
    # OS X
    cmd += '.exe'
    if not os.path.isfile(cmd):
        # 32-bit Windows
        cmd = os.path.join(directory, 'PCBuild', 'python_d.exe')
        if not os.path.isfile(cmd):
            # 64-bit Windows
            cmd = os.path.join(directory, 'PCBuild', 'AMD64', 'python_d.exe')
            if not os.path.isfile(cmd):
                print('CPython is not built')
                sys.exit(1)

subprocess.call([cmd, '-W', 'default', '-bb', '-E', '-m', 'test', '-r', '-w',
                 '-u', 'all', '-j', str(multiprocessing.cpu_count())])
