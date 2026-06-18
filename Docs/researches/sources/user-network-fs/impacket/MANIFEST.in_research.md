# sources/user-network-fs/impacket/MANIFEST.in

## Purpose

`MANIFEST.in` controls source distribution contents for Impacket packaging. It ensures top-level metadata, requirements, tox configuration, examples, and tests are included in generated sdists.

## Important APIs, Types, and Functions

The manifest uses setuptools/distutils directives: `include` for specific files (`LICENSE`, `README.md`, `SECURITY.md`, `TESTING.md`, `requirements.txt`, `tox.ini`, etc.) and `recursive-include` for `examples` and `tests`.

## Control Flow

When `setup.py sdist` runs, setuptools reads the manifest and adds matching files to the source distribution file list. This file does not affect wheel package data unless setup configuration also includes package data.

## State and Persistence Behavior

It influences build artifacts only. The persistent output is an sdist containing the included files. No runtime state is modified.

## Dependencies and Integration Points

It integrates with `setup.py`, CI wheel/source build workflows, PyPI releases, and downstream users who install from sdist or inspect bundled examples/tests.

## Risks and Edge Cases

`recursive-include examples tests *.txt *.py` is unusual because it names two directories before patterns; the later `recursive-include tests *` is broader and may duplicate intent. Files outside listed patterns, such as YAML, JSON, certificates, or binary test fixtures, may be excluded unless captured by other packaging metadata. Including all tests can enlarge source distributions.

## Test Signals

Run `python setup.py sdist` or modern `python -m build --sdist`, inspect the archive contents, and confirm required metadata, examples, and test fixtures are present. CI wheel build does not fully validate sdist completeness.
