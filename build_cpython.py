#!/usr/bin/env python
"""Build CPython"""
import multiprocessing
import os
import subprocess
import sys


def executable():
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
                    return None
    return os.path.abspath(cmd)


def main():
    if sys.platform == 'win32':
        print("See the devguide's Getting Set Up guide for building under "
              "Windows")

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
    return executable()

if __name__ == '__main__':
    if not main():
        print('No executable found')
        sys.exit(1)
