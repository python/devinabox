devinabox -- Bootstrapping a core Python sprint
===============================================

The **devinabox** project helps an experienced CPython developer produce a
directory which contains everything necessary to enable sprint participants
to get set up quickly (regardless of OS).

This README outlines two things:

- what to download to create a devinabox
- what is provided to help new contributors

This document provides instructions for sprint leaders; it does not provide
instructions for new contributors. If you are
a **new contributor**, ask your sprint leader(s) about how to get started.


Things to download to create a devinabox
========================================

The following sections outline various files to download and repositories to
clone into your devinabox including:

- version control tools
- compiler
- CPython
- PEPs
- Devguide
- coverage.py

Be careful **NOT** to change the destination directories that
repositories are cloned into. These default directory names are assumed by
the other files in devinabox.

When you are done you should have in the destination directory everything
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
hg.python.org which only core developers can use. It's easier to make the
clones from scratch.


Mercurial
---------

You will want to download the latest release of Mercurial
(http://pypi.python.org/pypi/Mercurial) and TortoiseHg for Windows users
(http://tortoisehg.bitbucket.org/download/). OS X users can be told that
Mercurial is available through Homebrew if they prefer
(if they use MacPorts or any other package manager ask them to use the
download of Mercurial you have provided to save time).

Providing Mercurial guarantees there is no issue with new contributors trying to
update repositories or generating patches.


A Compiler
-----------

If you receive questions about compilers, here are some suggestions.

OS X users should be told to download XCode from the Apple App Store **ahead of
time**. It's on the order of a couple GiB in size, so you don't want to have
people downloading it at the sprint. After installation they should also make
sure to install the command-line tools (e.g. in Mavericks,
``xcode-select --install``).

If new contributors think they may be doing C development, suggest the use of
LLVM + clang as this provides better error reporting than gcc.

For Windows users, ask them to download and install `Visual Studio Community
edition`_ **ahead of time**.

.. _Visual Studio Community edition: https://www.visualstudio.com/en-us/products/visual-studio-community-vs.aspx

CPython
-------

Clone the `CPython repository`_ and build it (you will be cleaning up your build
later, though as a final step).

Also make sure to build the documentation. This alleviates the need for
sprint participants to build it from scratch. To build the documentation, create a venv
with sphinx installed and point the Doc Makefile at the Python linked to in the
venv.

All of this can be done by doing::

  # Assuming at the root of the devinabox directory
  python build_cpython.py
  ./cpython/python -m venv venv
  ./venv/bin/pip install sphinx
  cd cpython/Doc
  make html PYTHON=../../venv/bin/python

.. _CPython repository: http://hg.python.org/cpython


PEPs
----

Clone the `PEP repository`_ and build it (use the venv you created to build the
CPython docs if necessary). This allows sprinters a local copy to reference
for a PEP and it allows using the easier-to-read HTML version.

No specific guidelines for building the PEPs are provided since there is only
a slim chance sprint participants will be editing a PEP.

.. _PEP repository: http://hg.python.org/peps


Devguide
--------

Clone the `devguide repository`_ and build it (again, use the venv created to
build the CPython docs if necessary). This gives sprinters a local copy to
use rather than having to use the (often slow) internet connection at the
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


Helpful files for sprint participants
=====================================

Helpful files are included in order to make things a little bit easier for
you, the sprint leader, as well as sprint participants and new contributors.


``index.html``
--------------

An HTML file with links to:

- documentation which you built previously
- the helper scripts


``build_cpython.py``
--------------------

On UNIX-based OSs this file builds the CPython repository. On all platforms it
verifies that the expected CPython binary exists.

While the devguide includes instructions on how to build under UNIX, this
script simplifies the process for sprint participants by having a single
command to configure and build CPython. It also uses reasonable defaults
(e.g. all cores on the CPU).
