# sources/distributed-fs/tahoe-lafs/src/allmydata/util/__init__.py

## Purpose

This package initializer is intentionally empty. Its role is structural: it marks `allmydata.util` as an importable Python package containing Tahoe-LAFS compatibility helpers, filesystem utilities, async helpers, encoding shims, transport providers, statistics, logging adapters, and cryptographic hash wrappers.

## APIs and control flow

The file exports no symbols, performs no imports, and has no runtime control flow. Importers reach utility modules directly, for example `allmydata.util.hashutil`, `allmydata.util.fileutil`, or `from allmydata.util import base32`. Because the initializer does not import submodules, importing `allmydata.util` has no side effects such as starting thread pools, touching platform APIs, installing logging observers, or importing optional Tor/I2P dependencies.

## State, dependencies, risks, and tests

There is no local state or persistence. The absence of eager imports is an integration choice: many sibling modules carry expensive or platform-sensitive side effects, including CPU thread-pool startup in `cputhreadpool.py`, Windows ctypes setup in `fileutil.py`, and optional dependency imports in provider modules.

The main risk is accidental future convenience imports in this file. Adding them could create import cycles, slow startup, or make optional dependencies mandatory. Test signals are mostly indirect: package import should succeed in minimal environments, direct submodule imports should continue to work, and packaging metadata should include this file so `allmydata.util` remains importable.
