# sources/user-network-fs/impacket/setup.py

## Purpose

`setup.py` is Impacket's setuptools packaging entry point. It defines package version metadata, dependencies, included packages, example scripts, classifiers, and platform-specific data files.

## Important APIs, Types, And Functions

Top-level constants include `PACKAGE_NAME`, `VER_MAJOR`, `VER_MINOR`, `VER_MAINT`, `VER_PREREL`, and computed `VER_LOCAL`. `read(fname)` reads files relative to the setup script. The final `setup()` call supplies metadata, long description, packages, scripts, data files, requirements, extras, and classifiers.

## Control Flow

At execution time the script probes Git availability. In a Git checkout it appends a local version suffix built from the latest commit date/time and short hash. Failure or non-Git source trees omit the suffix. Non-Darwin systems install README, LICENSE, and `doc/*` under `share/doc/impacket`; Darwin disables `data_files`. `setup()` then builds version `0.14.0.dev{local}`.

## State And Persistence Behavior

The script itself has no app state, but build/install commands create setuptools metadata, build artifacts, installed packages, scripts, and documentation files. It reads Git metadata and `README.md`.

## Dependencies And Integration Points

It depends on `setuptools`, `glob`, `os`, `platform`, and `subprocess`. Runtime dependencies include `pyasn1`, `pyasn1_modules`, `pycryptodomex`, `pyOpenSSL`, `six`, constrained `ldap3`, `ldapdomaindump`, `flask`, and `charset_normalizer`; Windows gets `pyreadline3`.

## Risks And Edge Cases

Git probing uses wildcard subprocess imports and `shell=True` for two commands. Version suffixes depend on repository state and Git availability. `read()` has no explicit encoding. Package lists are manually maintained, so new subpackages can be missed. Data-file installation differs by platform.

## Test Signals

Packaging tests should build from Git and non-Git trees, verify PEP 440 version strings, check subpackage inclusion, validate dependency constraints, and run build smoke tests on Linux, macOS, and Windows.
