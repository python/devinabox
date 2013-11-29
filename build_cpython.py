#!/usr/bin/env python
# Source is Python 2/3 compatible.
"""Build CPython on UNIX.

On all platforms, return the path to the executable.

"""
from __future__ import print_function

import os
import subprocess
import sys

try:
    from os import cpu_count
except ImportError:
    from multiprocessing import cpu_count


def executable(directory):
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
                    return None
    return os.path.abspath(cmd)


def main(directory):
    if sys.platform == 'win32':
        print("See the devguide's Getting Set Up guide for building under "
              "Windows")

    cwd = os.getcwd()
    os.chdir(directory)
    try:
        if os.path.isfile('Makefile'):
            print('Makefile already exists; skipping ./configure')
        else:
            subprocess.check_call(['./configure', '--prefix=/tmp/cpython',
                                   '--with-pydebug'])
        make_cmd = ['make', '-s', '-j', str(cpu_count())]
        subprocess.call(make_cmd)
    finally:
        os.chdir(cwd)
    return executable(directory)

if __name__ == '__main__':
    arg_count = len(sys.argv) - 1
    if arg_count > 1:
        raise ValueError(
                '0 or 1 arguments expected, not {}'.format(arg_count))
    elif arg_count == 1:
        directory = sys.argv[1]
    elif os.path.exists('cpython'):
        directory = 'cpython'
    else:
        directory = '.'
    executable = main(directory)
    if not executable:
        print('CPython executable NOT found')
    else:
        print('CPython executable can be found at:')
        print(' ', executable)
    sys.exit(0 if executable else 1)
