#!/usr/bin/env python3
"""Python-Dev In a Box: (almost) everything you need to contribute to (C)Python
in under 700 MB.

This script will create a directory which will end up containing (or remind you
to download) everything you need to contribute to (C)Python's development (sans
a C compiler) through the ``create`` command. You can also "build" what is
provided in the Box to save users some hassle (e.g., build the documentation).

Once a Box has been created, users of it can update what it contains (e.g.,
update the repository of CPython).

There are also some scripts provide along side this one to help get people
started. See the README for more information.

"""
import abc
import contextlib
from distutils.version import LooseVersion as Version
import os
import os.path
import subprocess
import urllib.request
import urllib.parse
import webbrowser
import xmlrpc.client


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
        subprocess.check_call(['hg', '-q', 'clone', self.url, self.directory])

    def update(self):
        """Update the Hg clone in 'directory'."""
        with change_cwd(self.directory):
            subprocess.check_call(['hg', '-q', 'pull'])
            subprocess.check_call(['hg', '-q', 'update'])


class SvnProvider(Provider):

    """Provide an svn checkout."""

    @abc.abstractproperty
    def url(self):
        """Location of the repository."""
        raise NotImplementedError

    def create(self):
        """Check out the svn repository to 'directory'."""
        subprocess.check_call(['svn', 'checkout', '-q',
                               self.url, self.directory])

    def update(self):
        """Update the svn checkout in 'directory'."""
        subprocess.check_call(['svn', 'update', '-q', self.directory])


class Visual_Studio_Express(Provider):

    """The Web installer for Visual C++ Express."""

    size = (4, None)
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
        self._prompt('download Visual C++ Express at {}'.format(url))


class CoveragePy(HgProvider):

    """Cloned repository for coverage.py so you can generate coverage report
    for the stdlib."""

    url = 'https://brettsky@bitbucket.org/ned/coveragepy'
    directory = 'coveragepy'
    size = (5, None)  # XXX coverage report for CPython

    # XXX build runs coverage tests


class Mercurial(Provider):

    """Provide Mercurial (source release) and TortoiseHg (for Windows) so you
    can update CPython's repository."""

    directory = 'Mercurial'
    size = (47, None)  # Includes TortoiseHg for 32/64-bit Windows

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
            # XXX
            pass

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
        self._prompt('Download TortoiseHg from {}'.format(url))

    def create(self):
        """Fetch the latest source distribution for Mercurial."""
        try:
            os.mkdir(self.directory)
        except OSError:
            pass
        self._create_mercurial()
        self._create_tortoisehg()



class Devguide(HgProvider):

    """Clone of the Python developer's guide so you know what to do."""

    size = (1, 4)

    url = 'http://hg.python.org/devguide'
    directory = 'devguide'

    def build(self):
        """Build the devguide and symlink its index page."""
        # Grab Sphinx from cpython/Doc/tools/
        tools_directory = os.path.join(CPython.directory, 'Doc', 'tools')
        orig_pythonpath = os.environ['PYTHONPATH']
        os.environ['PYTHONPATH'] = os.path.abspath(tools_directory)
        try:
            with change_cwd(self.directory):
                subprocess.check_call(['make', 'html'])
        finally:
            os.environ['PYTHONPATH'] = orig_pythonpath
        index_path = os.path.join(self.directory, '_build', 'html',
                                  'index.html')
        os.symlink(index_path, 'devguide.html')


class PEPs(SvnProvider):

    """Checkout the Python Enhancement Proposals so you have the style guides
    (PEPs 7 & 8) along with all other PEPs for reference."""

    url = 'http://svn.python.org/projects/peps/trunk/'
    directory = 'peps'
    size = (14, 20)

    def build(self):
        """Build the PEPs and symlink PEP 0."""
        with change_cwd(self.directory):
            subprocess.check_call(['make'])
        os.symlink(os.path.join(self.directory, 'pep-0000.html'), 'peps.html')


class CPython(HgProvider):

    """Clone of CPython (and requisite tools to build the documentation)."""

    url = 'http://hg.python.org/cpython'
    directory = 'cpython'
    size = (245,   # Includes stuff required to build docs/ docs built
            325)  # Only docs are built

    def create(self):
        """Clone CPython and get the necessary tools to build the
        documentation."""
        super().create()
        with change_cwd(os.path.join(self.directory, 'Doc')):
            subprocess.check_call(['make', 'checkout'])

    def build(self):
        cmd = 'make' if sys.platform != 'win32' else 'make.bat'
        with change_cwd(os.path.join(self.directory, 'Doc')):
                subprocess.check_call([cmd, 'html'])
        # XXX symlink to python_docs.html


if __name__ == '__main__':
    import argparse  # XXX snag from CPython repo if missing

    all_providers = (CPython, Devguide, PEPs, CoveragePy, Mercurial,
                     Visual_Studio_Express)
    parser = argparse.ArgumentParser(prog='Python-Dev In a Box')
    subparsers = parser.add_subparsers() # XXX help
    parser_create = subparsers.add_parser('create',
                                          help='Create a %(prog)s')
    parser_create.add_argument('--build', action='store_true', default=False)
    group = parser_create.add_mutually_exclusive_group()
    group.add_argument('--all', dest='providers', action='store_const',
                       const=all_providers,
                       help='Provide everything (the default)')
    group.add_argument('--basic', dest='providers', action='store_const',
                       const=(CPython, Devguide, PEPs, CoveragePy),
                       help='Provide the basics people probably are lacking')
    group.add_argument('--minimum', dest='providers', action='store_const',
                       const=(CPython, Devguide, PEPs),
                       help='Provide the bare minimum to be productive')
    # XXX --build option
    # XXX parser_update = subparsers.add_parser('update', help='Update the %(prog)s') # XXX also run build
