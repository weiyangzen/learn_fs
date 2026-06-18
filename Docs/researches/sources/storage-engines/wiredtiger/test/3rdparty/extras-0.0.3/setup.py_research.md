<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/extras-0.0.3/setup.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/extras-0.0.3/setup.py

Purpose: Setuptools installer metadata for the vendored `extras` package.

Important APIs/functions: Imports local `extras`, conditionally imports `testtools.TestCommand` through `extras.try_import`, defines `get_version` from `extras.__version__`, defines `get_long_description` reading `README.rst` beside setup.py, registers `cmdclass['test']` when testtools is present, and calls `setup` with package metadata and packages `extras` and `extras.tests`.

Control flow: Top-level import checks optional testtools command, computes metadata lazily through helper calls, and invokes setuptools.

State and persistence behavior: Packaging-time metadata/install artifacts only. It reads README and may enable a custom test command based on the current Python environment.

Dependencies and integration points: Depends on setuptools, local `extras`, optional testtools, and README.rst. WiredTiger's vendored test dependency setup can install this package locally.

Risks: Importing `extras` from setup relies on the local source directory being first on `sys.path`. The description contains a typo ("shold"). Optional test command behavior varies with installed dependencies. No explicit install_requires are declared for testtools despite tests needing it.

Test signals: `python setup.py egg_info`, `python setup.py test` when testtools is available, and package import after installation.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/extras-0.0.3/setup.py -->
