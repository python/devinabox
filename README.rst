devinabox -- Bootstrapping a Python core dev sprint
/////////////////////////////////////////////////////////

The devinabox project is meant to help a CPython core developer produce a
directory which contains everything necessary to enable someone at a sprint
(regardless of OS) to get set up quickly. This README is **NOT** meant for a new
contributor! If you *are* a new contributor, ask the core developer leading your
sprint about how to get started.

This README outlines two things: what to download to create a devinabox and what
is provided to help new contributors.


Stuff to download
=================

The following sections outline various files to download and repositories to
clone into your devinabox. Make sure to **NOT** change the directories that
repositories are cloned into. The default names are assumed by the other files
in devinabox.

When you are done you should have in this directory everything
someone needs to contribute. Simply copy the whole directory to some sort of
media (USB 3 drive and a CD tend to work well) and then pass it around for
people to copy somewhere on to their system. They can run ``hg pull -u`` to
get updates, sparing the probably taxed internet connection at the sprint from
doing complete repository cloning.

If recreating from an old checkout, ``hg purge --all`` in the individual
clones is a handy way to ensure old build artifacts have been removed.
You will need to enable the purge extension in ``~/.hgrc``.

Also make sure to not simply copy your own repositories to the box! Otherwise
the clones will most likely have paths which use SSH and the hg account on
hg.python.org which only core developers can use. It's just easier to make the
clones from scratch.


Mercurial
---------

You will want to download the latest release of Mercurial
(http://pypi.python.org/pypi/Mercurial) and TortoiseHg for Windows users
(http://tortoisehg.bitbucket.org/download/). OS X users can be told that
Mercurial is available through Homebrew if they prefer
(if they use MacPorts or any other package manager then tell them they
should switch to Homebrew at home as it handles Python the best and to use the
download of Mercurial you have provided to save time).

Providing Mercurial guarantees there is no issue with new contributors trying to
update repositories or generating patches.


A Compiler
-----------

Since you will most likely be dealing with developers this section is probably
not important, but just in case you get questions about compilers, here are some
suggestions.

OS X users should be told to download XCode from the Apple App Store **ahead of
time**. It's on the order of a couple GiB in size, so you don't want to have
people downloading it at the sprint. After installation they should also make
sure to install the command-line tools (e.g. in Mavericks,
``xcode-select --install``).

If new contributors think they may be doing C development, suggest LLVM + clang
for better error reporting than gcc.

For Windows users, tell them to download and install Visual C++ Express
(http://www.microsoft.com/express/Downloads/) **ahead of time**.


CPython
-------

Clone the `CPython repository`_ and build it (you will be cleaning up your build
later, though as a final step).

Also make sure to build the documentation. This alleviates the need for
everyone to build it from scratch. To build the documentation, create a venv
with sphinx installed and point the Doc Makefile at the Python linked to in the
venv.

All of this can be done by doing::

  # Assuming at the top of the devinabox.
  python build_cpython.py
  ./cpython/python -m venv venv
  ./venv/bin/pip install sphinx
  cd cpython/Doc
  make html PYTHON=../../venv/bin/python

.. _CPython repository: http://hg.python.org/cpython


PEPs
----

Clone the `PEP repository`_ and build it (use the venv you created to build the
CPython docs if necessary). That way if people need to reference a
PEP they can easily find itand will be able to use the easier-to-read HTML
version.

No specific guidelines for building the PEPs are provided for new contributors
since there is only a slim chance they will be editing a PEP, and if they are
then they should be able to figure out how to get the PEPs to build on their
own.

.. _PEP repository: http://hg.python.org/peps


Devguide
--------

Clone the `devguide repository`_ and build it (again, use the venv created to
build the CPython docs if necessary). This gives people a local copy to
use rather than having to use the (probably slow) internet connection at the
sprint.

.. _devguide repository: http://hg.python.org/devguide


Coverage.py
-----------

#. Download coverage_ (need a special file that is not part of the normal
   distribution of coverage, so can't just use pip)
#. Build CPython: ``./build_cpython.py``
#. Create an venv: ``./cpython/python -m venv venv``
#. Extract coverage: ``tar -x -f coverage-*.tar.gz``
#. Install coverage in the venv: ``./venv/bin/python coverage-*/setup.py install``
#. Set PYTHONPATH to ``fullcoverage`` (need to change your directory to the venv):
   ``export PYTHONPATH=../coverage-N.N/coverage/fullcoverage``
#. ``unset CPPFLAGS`` in order to avoid using system Python header files
#. Run coverage from the venv: ``./bin/python -m coverage run --pylib -m test``
#. Unset PYTHONPATH: ``unset PYTHONPATH``
#. Generate coverage report: ``./bin/python -m coverage html --directory=../coverage_report -i --include="../cpython/Lib/*" --title="CPython test coverage report"``

Do be aware that this step takes a few **hours**. If you find report generation
is the bottleneck you can try using PyPy3 or your installed Python 3 interpreter
to generate the report.

.. _setuptools: https://pypi.python.org/pypi/setuptools
.. _coverage: https://pypi.python.org/pypi/coverage


Included files to help out
==========================

A couple of files are included in order to make things a little bit easier for
both you and the new contributors.


``index.html``
--------------

An HTML file with links to the various pieces of documentation you built
previously and the helper scripts.


``build_cpython.py``
--------------------
On UNIX-based OSs it builds the CPython repository. On all platforms it
verifies that the expected CPython binary exists.

While the devguide includes instructions on how to build under UNIX, the script
just simplifies this by having a single command subsume both the configure and
build steps. It also uses reasonable defaults (e.g. all cores on the CPU).
