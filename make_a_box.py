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

    def _prompt(self, message):
        """Prompt the user to perform an action, waiting for a response."""
        input("{} [press Enter when done]".format(message))

    @abc.abstractmethod
    def create(self):
        """Create what is to be provided."""
        raise NotImplementedError

    def build(self):
        """Optional step to "build" something."""

    def update(self):
        """Update what is provided."""
        pass


class HgProvider(Provider):

    """Provide an Hg repository."""

    @abc.abstractproperty
    def url(self):
        """Location of the repository."""
        raise NotImplementedError

    def create(self):
        """Clone an Hg repository to 'directory'."""
        subprocess.check_call(['hg', 'clone', self.url, self.directory])


class SvnProvider(Provider):

    """Provide an svn checkout."""

    @abc.abstractproperty
    def url(self):
        """Location of the repository."""
        raise NotImplementedError

    def create(self):
        """Check out the svn repository to 'directory'."""
        subprocess.check_call(['svn', 'checkout', self.url, self.directory])


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


# XXX test
@rename('coverage.py')
class CoveragePy(HgProvider):

    """Cloned repository of coverage.py (WARNING: building takes a while)"""

    url = 'https://brettsky@bitbucket.org/ned/coveragepy'
    directory = 'coveragepy'
    size = 133  # Includes the coverage report

    def build(self):
        """Run coverage over CPython."""
        # Build Python
        executable = build_cpython.main()
        # Run coverage
        if not executable:
            print('No CPython executable found')
            sys.exit(1)
        print('Running coverage ...')
        regrest_path = os.path.join(CPython.directory, 'Lib', 'test',
                                    'regrtest.py')
        subprocess.check_call([executable, self.directory, 'run', '--pylib',
                               regrtest_path])
        # ``make distclean`` as you don't want to distribute your own build
        with change_cwd(CPython.directory):
            subprocess.check_call(['make', 'distclean'])
        # Generate the HTML report
        print('Generating report ...')
        subprocess.call([executable, 'coveragepy', 'html', '-i', '--omit',
                         '"*/test/*,*/tests/*"', '-d', 'coverage_report'])


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
        try:
            return release_data['download_url']
        except KeyError:
            print('Mercurial has changed how it releases software on PyPI; '
                  'please report this to bugs.python.org')
            sys.exit(1)

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


class PEPs(SvnProvider):

    """Checkout of the Python Enhancement Proposals (for PEPs 7 & 8)"""

    url = 'http://svn.python.org/projects/peps/trunk/'
    directory = 'peps'
    size = 20

    def build(self):
        """Build the PEPs."""
        with change_cwd(self.directory):
            subprocess.check_call(['make'])


class Devguide(HgProvider):

    """Clone of the Python Developer's Guide"""

    size = 4

    url = 'http://hg.python.org/devguide'
    directory = 'devguide'

    def build(self):
        """Build the devguide using Sphinx from CPython's docs."""
        # Grab Sphinx from cpython/Doc/tools/
        tools_directory = os.path.join(CPython.directory, 'Doc', 'tools')
        orig_pythonpath = os.environ.get('PYTHONPATH')
        os.environ['PYTHONPATH'] = os.path.abspath(tools_directory)
        try:
            with change_cwd(self.directory):
                subprocess.check_call(['make', 'html'])
        finally:
            if orig_pythonpath:
                os.environ['PYTHONPATH'] = orig_pythonpath
        index_path = os.path.join(self.directory, '_build', 'html',
                                  'index.html')


class CPython(HgProvider):

    """Clone of CPython (and requisite tools to build the documentation)"""

    url = 'http://hg.python.org/cpython'
    directory = 'cpython'
    size = 330  # Only docs are built

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
    print('Please choose what to provide [y/n]:\n')
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
        for provider in desired_providers:
            ins = provider()
            print('Fetching {} ...'.format(provider.__name__))
            ins.create()
            print('Building {} ...'.format(provider.__name__))
            ins.build()
    with open('README', 'w') as file:
        header = 'Python-Dev In a Box: created on {}\n'
        file.write(header.format(datetime.date.today()))
    sys.exit(0)
