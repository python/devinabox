#!/usr/bin/env python3
"""Python-Dev In a Box: everything you need to contribute to Python in under
700 MB.

This script will clone, checkout, download, or ask you to download everything
you need to contribute to (C)Python's development short of a C compiler. It
will also "build" everything so that users do not need to do **everything**
from scratch. This also allows for easy offline use.

There are also some scripts provided along side this one to help in executing
common tasks.

"""
import abc
import contextlib
import datetime
from distutils.version import LooseVersion as Version
import operator
import os
import os.path
import shutil
import subprocess
import sys
import urllib.request
import urllib.parse
import webbrowser
import xmlrpc.client
import build_cpython


def rename(new_name):
    """Decorator to rename an object that defines __name__."""
    def do_rename(ob):
        ob.__name__ = new_name
        return ob
    return do_rename


@contextlib.contextmanager
def change_cwd(directory):
    cwd = os.getcwd()
    os.chdir(directory)
    try:
        yield
    finally:
        os.chdir(cwd)


class Provider(metaclass=abc.ABCMeta):

    """Base class for items to be provided."""

    @abc.abstractproperty
    def directory(self):
        """Directory to put everything."""
        raise NotImplementedError

    @abc.abstractproperty
    def size(self):
        """Size of what is provided (built and everything)."""
        raise NotImplementedError

    def _prompt(self, message):
        """Prompt the user to perform an action, waiting for a response."""
        input("{} [press Enter when done]".format(message))

    @abc.abstractmethod
    def create(self):
        """Create what is to be provided."""
        raise NotImplementedError

    def build(self):
        """Optional step to "build" something."""


class HgProvider(Provider):

    """Provide an Hg repository."""

    @abc.abstractproperty
    def url(self):
        """Location of the repository."""
        raise NotImplementedError

    @property
    def directory(self):
        return os.path.abspath(os.path.basename(self.url))

    def create(self):
        """Clone an Hg repository to 'directory'."""
        if os.path.exists(self.directory):
            subprocess.check_call(['hg', 'pull', '-u', self.url],
                                  cwd=self.directory)
        else:
            subprocess.check_call(['hg', 'clone', self.url, self.directory])


@rename('Visual C++ Express')
class VisualCPPExpress(Provider):

    """The Web installer for Visual C++ Express"""

    size = 4
    directory = 'Visual C++ Express'

    def create(self):
        """Bring up a browser window to download the release."""
        try:
            os.mkdir(self.directory)
        except OSError:
            pass
        url = 'http://www.microsoft.com/express/Downloads/'
        try:
            webbrowser.open(url)
        except webbrowser.Error:
            pass
        self._prompt('download Visual C++ Express at {} and put in {}'.format(
                        url, self.directory))


@rename('coverage.py')
class CoveragePy(HgProvider):

    """Clone of coverage.py (WARNING: building takes a while)"""

    url = 'https://bitbucket.org/ned/coveragepy'
    size = 133  # Includes the coverage report
    docs = os.path.join('coverage_report', 'index.html')

    @contextlib.contextmanager
    def build_cpython(self):
        self.executable = build_cpython.main()
        if not self.executable:
            print('No CPython executable found')
            sys.exit(1)
        self.cpython_dir = os.path.dirname(self.executable)
        yield
        print('Cleaning up the CPython build ...')
        subprocess.check_call(['make', 'distclean'])

    @contextlib.contextmanager
    def build_coveragepy(self):
        env = os.environ.copy()
        env['CPPPATH'] = '-I {} -I {}'.format(self.cpython_dir,
                                     os.path.join(self.cpython_dir, 'Include'))
        with change_cwd(self.coveragepy_dir):
            print('Compiling coverage.py extension(s) ...')
            cmd = [self.executable, 'setup.py', 'build_ext', '--inplace']
            subprocess.check_call(cmd, env=env)
            yield
            # XXX clean up tracer.so; distribute?

    def generate_coveragepy_command(self, command, *args):
        return [self.executable, self.coveragepy_dir, command,
                '--include', os.path.join(self.cpython_dir, 'Lib', '*'),
                '--omit', '"Lib/test/*,Lib/*/tests/*"'] + list(args)

    @contextlib.contextmanager
    def run_coveragepy(self):
        print('Running coverage ...')
        regrtest_path = os.path.join(self.cpython_dir, 'Lib', 'test',
                                     'regrtest.py')
        fullcoverage = os.path.join(self.coveragepy_dir, 'coverage',
                                    'fullcoverage')
        env = os.environ.copy()
        env['PYTHONPATH'] = fullcoverage
        cmd = self.generate_coveragepy_command('run', '--pylib', regrtest_path,
                                               'test_imp')
        subprocess.check_call(cmd, env=env)
        yield
        os.unlink('.coverage')

    def report_coveragepy(self):
        print('Generating report ...')
        cmd = self.generate_coveragepy_command('html', '-i', '-d',
                                os.path.join(self.root_dir, 'coverage_report'))
        subprocess.check_call(cmd)

    def build(self):
        """Run coverage over CPython."""
        self.coveragepy_dir = self.directory
        self.root_dir = os.path.dirname(self.directory)
        with self.build_cpython(), self.build_coveragepy():
            with change_cwd(self.cpython_dir):
                with self.run_coveragepy():
                    self.report_coveragepy()


class Mercurial(Provider):

    """Source release of Mercurial along with TortoiseHg"""

    directory = 'Mercurial'
    size = 47  # Includes TortoiseHg for 32/64-bit Windows

    def _download_url(self):
        """Discover the URL to download Mercurial from."""
        pypi = xmlrpc.client.ServerProxy('http://pypi.python.org/pypi')
        hg_versions = pypi.package_releases('Mercurial')
        hg_versions.sort(key=Version)
        latest_release = hg_versions[-1]
        # Mercurial keeps releases on their servers
        release_data = pypi.release_data('Mercurial', latest_release)
        fname = "mercurial-%s.tar.gz" % latest_release
        try:
            release_url = release_data['download_url']
        except KeyError:
            print('Mercurial has changed how it releases software on PyPI; '
                  'please report this to bugs.python.org')
            sys.exit(1)
        return os.path.join(release_url, fname)

    def _url_filename(self, url):
        """Find the filename from the URL."""
        return os.path.split(urllib.parse.urlparse(url).path)[1]

    def _create_mercurial(self):
        """Download the latest source release of Mercurial."""
        file_url = self._download_url()
        file_name = self._url_filename(file_url)
        with urllib.request.urlopen(file_url) as url_file:
            with open(os.path.join(self.directory, file_name), 'wb') as file:
                file.write(url_file.read())

    def _create_tortoisehg(self):
        """Open a web page to the TortoiseHg download page."""
        url = 'http://tortoisehg.bitbucket.org/download/'
        try:
            webbrowser.open(url)
        except webbrowser.Error:
            pass
        self._prompt('Download TortoiseHg from {} and put in {}'.format(url,
                         self.directory))

    def create(self):
        """Fetch the latest source distribution for Mercurial."""
        try:
            os.mkdir(self.directory)
        except OSError:
            pass
        self._create_mercurial()
        self._create_tortoisehg()


class PEPs(HgProvider):

    """Checkout of the Python Enhancement Proposals (for PEPs 7 & 8)"""

    url = 'http://hg.python.org/peps'
    size = 20
    docs = os.path.join('peps', 'pep-0000.html')

    def build(self):
        """Build the PEPs."""
        with change_cwd(self.directory):
            subprocess.check_call(['make'])


class Devguide(HgProvider):

    """Clone of the Python Developer's Guide"""

    size = 4

    url = 'http://hg.python.org/devguide'
    docs = os.path.join('devguide', '_build', 'html', 'index.html')

    def build(self):
        """Build the devguide using Sphinx from CPython's docs."""
        # Grab Sphinx from cpython/Doc/tools/
        tools_directory = os.path.join('cpython', 'Doc', 'tools')
        sphinx_build_path = os.path.join(tools_directory, 'sphinx-build.py')
        sphinx_build_path = os.path.abspath(sphinx_build_path)
        orig_pythonpath = os.environ.get('PYTHONPATH')
        os.environ['PYTHONPATH'] = os.path.abspath(tools_directory)
        orig_sphinxbuild = os.environ.get('SPHINXBUILD')
        os.environ['SPHINXBUILD'] = 'python {}'.format(sphinx_build_path)
        try:
            with change_cwd(self.directory):
                subprocess.check_call(['make', 'html'])
        finally:
            if orig_pythonpath:
                os.environ['PYTHONPATH'] = orig_pythonpath
            if orig_sphinxbuild:
                os.environ['SPHINXBUILD'] = orig_sphinxbuild
        index_path = os.path.join(self.directory, '_build', 'html',
                                  'index.html')


class CPython(HgProvider):

    """Clone of CPython (and requisite tools to build the documentation)"""

    url = 'http://hg.python.org/cpython'
    size = 330  # Only docs are built
    docs = os.path.join('cpython', 'Doc', 'build', 'html', 'index.html')

    def create(self):
        """Clone CPython and get the necessary tools to build the
        documentation."""
        super().create()
        with change_cwd(os.path.join(self.directory, 'Doc')):
            # XXX Windows?
            subprocess.check_call(['make', 'checkout'])

    def build(self):
        """Build CPython's documentation.

        CPython itself is not built as one will most likely not want to
        distribute that on a CD. The build_cpython.py script can be used by the
        Box user for building CPython.

        """
        cmd = 'make' if sys.platform != 'win32' else 'make.bat'
        with change_cwd(os.path.join(self.directory, 'Doc')):
                subprocess.check_call([cmd, 'html'])


if __name__ == '__main__':
    all_providers = (CPython, Devguide, PEPs, CoveragePy, Mercurial,
                     VisualCPPExpress)
    print(__doc__)
    print('Please choose what to provide [answer y/n]:\n')
    desired_providers = []
    for provider in all_providers:
        docstring = provider.__doc__#.replace('\n', ' ')
        msg = '{} ({} MB built)? '.format(docstring, provider.size)
        response = input(msg)
        if response in ('Y', 'y'):
            desired_providers.append(provider)
    print()
    getting = ', '.join(map(operator.attrgetter('__name__'),
                            desired_providers))
    print('Getting {}'.format(getting))
    total_size = sum(map(operator.attrgetter('size'), desired_providers))
    msg = 'The requested Box will be about {} MB. OK? [y/n] '.format(total_size)
    response = input(msg)
    if response not in ('Y', 'y'):
        sys.exit(0)
    else:
        print()
        for provider in desired_providers:
            ins = provider()
            print('Fetching {} ...'.format(provider.__name__))
            ins.create()
            print('Building {} ...'.format(provider.__name__))
            ins.build()
    with open('README', 'w') as file:
        header = 'Python-Dev In a Box: created on {}\n'
        file.write(header.format(datetime.date.today()))
        file.write('\n')
        file.write('Documentation indices can be found at:\n')
        for provider in desired_providers:
            if hasattr(provider, 'docs'):
                file.write('  {}\n'.format(provider.docs))
    sys.exit(0)
