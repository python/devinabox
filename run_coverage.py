#!/usr/bin/env python
"""Create a coverage report for CPython"""
import subprocess
import os
import sys
import build_cpython
import run_tests


def main():
    build_cpython.main()
    executable = run_tests.executable()
    if not executable:
        print('no CPython executable found')
        sys.exit(1)

    print('Running coverage ...')
    subprocess.check_call([executable, 'coveragepy', 'run', '--pylib',
                           os.path.join('cpython', 'Lib', 'test', 'regrtest.py'),
                          ])
    print('Generating report ...')
    subprocess.call([executable, 'coveragepy', 'html', '-i', '--omit',
                     '"*/test/*,*/tests/*"', '-d', 'coverage_report'])
    print('Creating symlink ...')
    os.symlink(os.path.join('coverage_report', 'index.html'), 'coverage.html')


if __name__ == '__main__':
    main()
