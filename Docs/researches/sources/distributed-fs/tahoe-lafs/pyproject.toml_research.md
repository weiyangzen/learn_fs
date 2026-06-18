# sources/distributed-fs/tahoe-lafs/pyproject.toml

## Purpose

This is the package, build, dependency, script, and optional-extra definition for Tahoe-LAFS. It declares project metadata, runtime requirements, command entry points, optional Tor/I2P/build/test dependencies, hatch-vcs versioning, and wheel contents.

## Important APIs, Types, And Functions

The `[project]` table names the package `tahoe-lafs`, uses dynamic versioning, requires Python `>=3.9`, declares GPL-related licensing, and lists classifiers. `dependencies` is the core runtime contract: zfec, zope.interface, Foolscap, cryptography, pyOpenSSL, Twisted with `tls,conch`, PyYAML, six, magic-wormhole, eliot, attrs, Autobahn, Klein/Werkzeug/treq, CBOR/CDDL libraries, Click, psutil, filelock, Windows `pywin32`, and Python 3.13 `legacy-cgi`. `[project.scripts]` exposes `tahoe` and `grid-manager`. Optional extras cover `tor`, `i2p`, `build`, `testenv`, and `test`. Hatch configuration derives versions from VCS tags and writes `src/allmydata/_version.py`; build include/exclude lists define source distributions and wheels.

## Control Flow

Build frontends read `[build-system]`, load hatchling and hatch-vcs, calculate a version from tags matching `tahoe-lafs-(.*)`, and package `src/allmydata` into wheels. Installers resolve project dependencies and extras. Console-script generation points invocations to `allmydata.scripts.runner:run` and `allmydata.cli.grid_manager:grid_manager`.

## State And Persistence

The file persists dependency and packaging policy. It can generate persistent build artifacts and `_version.py` during build hooks, but it has no direct application runtime state.

## Dependencies And Integration Points

It is the central integration point for pip, build, hatchling, hatch-vcs, console scripts, CI, optional anonymity transports, the SFTP frontend, web frontend, and test tooling. Comments encode compatibility history for Foolscap, Twisted, cryptography, Werkzeug, cbor2, and Paramiko.

## Risks

Dependency comments document several fragile compatibility edges. Broad dependencies without upper bounds can admit regressions, while testenv pins can become stale. `Twisted[tls,conch]` is intentionally used to satisfy SFTP/manhole constraints, so changing extras can break SFTP installs. The direct Chutney git dependency in the test extra depends on external network and repository availability. Build include/exclude lists must stay synchronized with repository layout.

## Test Signals

Signals include `python -m build`, wheel install smoke tests, `tahoe --help`, `grid-manager --help`, extras resolution for `tor`, `i2p`, and `test`, and CI coverage across supported Python versions 3.9 through 3.12 plus any Python 3.13 compatibility lane.
