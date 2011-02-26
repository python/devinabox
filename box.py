"""Python-Dev In a Box: (almost) everything you need to contribute to (C)Python
in under 700 MB.

This script will create a directory which will end up containing (or remind you
to download) everything you need to contribute to (C)Python's development (sans
a compiler):

    * Mercurial: source download
        Hg is Python's VCS (Version Control System).

    * TortoiseHg: Windows 32/64
        For ease-of-use for Windows users.

    * Visual C++ Express: English Web installer
        So Windows users can compile CPython.
        OS X users should install XCode (http://developer.apple.com/) and
        optionally Homebrew (http://mxcl.github.com/homebrew/) to install
        LLVM/clang.
        Linux user should install gcc or clang using their distribution's
        package managers.

    * Python Developer's Guide
        "The devguide"; documentation on how to contribute to Python.

    * Python Enhancement Proposals
        Also known as PEPs. This is included as reference material, especially
        for PEPs 7 & 8 (the C and Python style guides, respectively).

    * CPython
        The included repository clone has branches for all versions of Python
        either under development or maintenance.

    * coverage.py: cloned repository
        For measuring the coverage of Python's test suite. Includes a
        cloned repository instead of the latest release as cutting-edge support
        is occasionally needed to support the in-development version of Python.

Once the requisite code has been checked out, various optional steps can be
performed to make the lives of users easier:

    * Update all cloned repositories (devguide, PEPs, CPython, coverage.py)

    * Build Python's documentation (will also lead to the download of the
    required software; requires Python to already be installed on the user's
    machine)

    * Build the devguide (requires Python's docs to be built so as to have a
    copy of Sphinx available to use)

    * Build the PEPs (requires Python to be installed)

    * Generate a coverage report (requires that CPython be built)


This script is assumed to be run by a built version of the in-development
version of CPython.

"""
# XXX README or just the docstring for this script?
# XXX script to build CPython? multiprocessing.cpu_count(). Windows?
# XXX script to run unit tests? multiprocessing.cpu_count()

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
        subprocess.check_call(['hg', 'clone', self.url, self.directory])

    def update(self):
        """Update the Hg clone in 'directory'."""
        with change_cwd(self.directory):
            subprocess.check_call(['hg', 'pull'])
            subprocess.check_call(['hg', 'update'])


class SvnProvider(Provider):

    """Provide an svn checkout."""

    @abc.abstractproperty
    def url(self):
        """Location of the repository."""
        raise NotImplementedError

    def create(self):
        """Check out the svn repository to 'directory'."""
        subprocess.check_call(['svn', 'checkout', self.url, self.directory])

    def update(self):
        """Update the svn checkout in 'directory'."""
        subprocess.check_call(['svn', 'update', self.directory])


class Visual_Studio_Express(Provider):

    """Provide the Web installer for Visual C++ Express."""

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

    """Cloned repository for coverage.py."""

    url = 'https://brettsky@bitbucket.org/ned/coveragepy'
    directory = 'coveragepy'
    size = (5, None)  # XXX coverage report for CPython

    # XXX script to run coverage tests?
    # XXX 'coverage' runs coverage tests


class Mercurial(Provider):

    """Provide Mercurial (source release) and TortoiseHg (for Windows)."""

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

    """Clone the Python developer's guide."""

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

    """Checkout the Python Enhancement Proposals."""

    url = 'http://svn.python.org/projects/peps/trunk/'
    directory = 'peps'
    size = (14, 20)

    def build(self):
        """Build the PEPs and symlink PEP 0."""
        with change_cwd(self.directory):
            subprocess.check_call(['make'])
        os.symlink(os.path.join(self.directory, 'pep-0000.html'), 'peps.html')


class CPython(HgProvider):

    """Clone CPython (and requisite tools to build the documentation)."""

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
        with change_cwd(os.path.join(self.directory, 'Doc'):
                subprocess.check_call([cmd, 'html'])


if __name__ == '__main__':
    import argparse
    parser = arparse.ArgumentParser(prog='Python-Dev In a Box')
    subparsers = parser.add_subparsers() # XXX help
    parser_create = subparsers.add_parser('create')  # XXX help
    # XXX --all option
    # XXX --basic option (everything that doesn't require a Web browser)
    # XXX --miniumum option (cpython, devguide, peps)
    # XXX --build option
    # XXX --with-coverage option
    parser_update = subparsers.add_parser('update')  # XXX help
    # XXX also run build (--with-coverage)



    for provider in (CPython, Devguide, PEPs, Mercurial, CoveragePy,
                     Visual_Studio_Express,):
        print('Creating', provider.__name__.replace('_', ' '))
        provider().create()
        print()
