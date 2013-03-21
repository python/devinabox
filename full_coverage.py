"""Use coverage.py on CPython's standard library.

See the ``-h`` or ``help`` command of the script for instructions on use.

"""
import importlib.machinery
import contextlib
import os
import shutil
import subprocess
import sys
import webbrowser


def path_from_here(path):
    """Calculate the absolute path to 'path' from where this file is located."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), path))

COVERAGE = path_from_here('coveragepy')
REPORT = path_from_here('coverage_report')
CPYTHON = os.path.dirname(sys.executable)


@contextlib.contextmanager
def chdir(directory):
    """Change the directory temporarily."""
    original_directory = os.getcwd()
    os.chdir(directory)
    yield
    os.chdir(original_directory)


def build(args):
    """Build coverage.py's C-based tracer.

    Make sure to delete any pre-existing build to make sure it uses the latest
    source from CPython.
    """
    with chdir(COVERAGE):
        for ext in importlib.machinery.EXTENSION_SUFFIXES:
            tracer_path = os.path.join('coverage', 'tracer' + ext)
            try:
                os.unlink(tracer_path)
            except FileNotFoundError:
                pass
        subprocess.check_call([sys.executable, 'setup.py', 'clean'])
        env = os.environ.copy()
        env['CPPFLAGS'] = '-I {} -I {}'.format(CPYTHON,
                                               os.path.join(CPYTHON, 'Include'))
        command = [sys.executable, 'setup.py', 'build_ext', '--inplace']
        process = subprocess.Popen(command, env=env)
        process.wait()


def run(args):
    """Run coverage.py against Python's stdlib as best as possible.

    If any specific tests are listed, then limit the run to those tests.
    """
    command = [sys.executable, COVERAGE, 'run', '--pylib', 'Lib/test/regrtest.py']
    if args.tests:
        command.extend(args.tests)
    with chdir(CPYTHON):
        try:
            os.unlink(os.path.join(CPYTHON, '.coverage'))
        except FileNotFoundError:
            pass
        pythonpath = os.path.join(COVERAGE, 'coverage', 'fullcoverage')
        process = subprocess.Popen(command, env={'PYTHONPATH': pythonpath})
        process.wait()


def report(args):
    """Generate the HTML-based coverage report.

    Write the results to either REPORT or a user-specified location.
    """
    report = os.path.abspath(args.directory)
    title = '{} {} test coverage'.format(sys.implementation.name,
                           sys.version.partition(' \n')[0])
    if os.path.exists(report):
        shutil.rmtree(report)
    with chdir(CPYTHON):
        subprocess.check_call([sys.executable, COVERAGE, 'html', '-i',
                               '-d', report, '--omit', 'Lib/test/*',
                               '--title', title])
    print(os.path.join(report, 'index.html'))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='subparser_name',
            help="use coverage.py on Python's standard library")

    build_parser = subparsers.add_parser('build',
            help='build coverage.py using {}'.format(sys.executable))
    build_parser.set_defaults(func=build)

    stdlib_path = os.path.join(CPYTHON, 'Lib')
    run_parser = subparsers.add_parser('run',
            help='run coverage.py over the standard library at {} '
                 '(coverage.py must already be built)'.format(stdlib_path))
    run_parser.add_argument('tests', action='store', nargs='*',
            help='optional list of tests to run (default: all tests)')
    run_parser.set_defaults(func=run)

    report_parser = subparsers.add_parser('html',
            help='generate an HTML coverage report')
    report_parser.add_argument('directory',
            help='where to save the report (default: {})'.format(REPORT),
            nargs='?', action='store', default=REPORT)
    report_parser.set_defaults(func=report)

    help_parser = subparsers.add_parser('help',
            help='show the help message for the specified command')
    help_parser.add_argument('command', nargs='?',
            help='for which command to show a help message')

    args = parser.parse_args()
    if args.subparser_name != 'help':
        args.func(args)
    else:
        help_args = ['-h']
        if args.command:
            help_args.insert(0, args.command)
        parser.parse_args(help_args)