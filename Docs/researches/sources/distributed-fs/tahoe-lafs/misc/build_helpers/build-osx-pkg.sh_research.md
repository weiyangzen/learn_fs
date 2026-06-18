# sources/distributed-fs/tahoe-lafs/misc/build_helpers/build-osx-pkg.sh

## Purpose

This shell script builds the legacy macOS Tahoe-LAFS installer package. It creates a Python 2.7 virtualenv, installs the current project, rewrites the generated `tahoe` entry point so it resolves libraries from `/Applications/tahoe.app`, and invokes Apple packaging tools to produce `tahoe-lafs-$VERSION-osx.pkg`.

## Important APIs, Types, and Functions

The script is procedural. `VERSION` is extracted from `src/allmydata/_version.py` using shell text filters. `TARGET` is fixed to `/Applications/tahoe.app`. External tools are the effective API surface: `virtualenv`, `pip install .`, `pkgbuild`, and `productbuild`.

## Control Flow

It removes `_trial_temp`, creates `osx-venv`, installs Tahoe, removes all virtualenv bin scripts, writes a custom `bin/tahoe` launcher, creates a `zope/__init__.py` workaround, copies `misc/build_helpers/osx/Contents`, builds an intermediate component package with scripts and install location, wraps it with `Distribution.xml`, and deletes `tahoe-lafs.pkg`.

## State, Dependencies, Integration, Risks, and Tests

State is entirely filesystem side effects: `osx-venv`, generated launcher, intermediate package, final package, and cleanup. Integration points are `test-osx-pkg.py`, `Distribution.xml`, and the pre/postinstall scripts. Risks include hard-coded Python 2.7 and `/Applications/tahoe.app`, fragile version parsing, lack of `set -e`, shell word splitting on paths, and a launcher that is less isolated than a real virtualenv. Tests should verify the produced package installs the expected app tree and that `bin/tahoe --version-and-path` loads dependencies from the packaged tree.
