# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/MANIFEST.in

## Purpose

`MANIFEST.in` controls the source distribution payload for this vendored Python package. It is intentionally small and mostly prunes non-Python build-system leftovers from the upstream multi-language subunit project while explicitly including `NEWS`.

## Important APIs, Types, and Functions

This is declarative setuptools manifest syntax rather than executable Python. It uses `exclude` for files such as `.gitignore`, `aclocal.m4`, `configure*`, `Makefile*`, `INSTALL`, `install-sh`, `missing`, `py-compile`, `stamp-h1`, and libtool/autotools helper names; `prune` for directories such as `autom4te.cache`, `c`, `c++`, `compile`, `m4`, `perl`, and `shell`; and `include NEWS` to keep the changelog in the sdist.

## Control Flow

During `setuptools` sdist generation, manifest commands are applied in order to the file list. The file removes generated/autotools and non-Python implementation artifacts, then restores `NEWS` as package documentation. Runtime import and test execution never read this file.

## State and Persistence Behavior

The file persists package assembly policy only. It does not create runtime state, but it determines what can be reconstructed from a source archive. If a needed Python package file is excluded here, builds from sdist could be incomplete even when the working tree is healthy.

## Dependencies and Integration Points

It integrates with setuptools via `pyproject.toml` and `setup.py`. It also reflects upstream subunit's mixed-language layout: the vendored Python package only needs the Python tree, packaging metadata, license/readme/news, and generated egg-info files, not C/C++/Perl/shell sources.

## Risks and Test Signals

The main risk is accidental omission from source distributions, especially if new Python-side data files or console script assets are added without updating the manifest. A useful validation signal is `python3 -m build --sdist` followed by checking the tarball contains `python/subunit`, `setup.py`, `setup.cfg`, `pyproject.toml`, `PKG-INFO`, licenses, and `NEWS`, while excluding pruned upstream-language directories.
