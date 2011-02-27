#!/usr/bin/env python
"""Run CPython's test suite in the most rigorous way possible."""
import multiprocessing
import subprocess
import sys
import build_cpython


def main():
    cmd = build_cpython.main()
    if cmd is None:
        print('CPython is not built')
        sys.exit(1)
    try:
        subprocess.call([cmd, '-W', 'default', '-bb', '-E', '-m', 'test', '-r',
                         '-w', '-u', 'all', '-j',
                         str(multiprocessing.cpu_count())])
    finally:
        os.rmdir('build')


if __name__ == '__main__':
    main()
