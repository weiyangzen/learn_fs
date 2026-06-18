## sources/user-network-fs/pyfuse3/MANIFEST.in

Purpose: Source distribution manifest for pyfuse3.

Important APIs/types/functions: Includes changes/license, grafts docs, headers, examples, rst, util, and tests, prunes test cache and `.github`, excludes manifest/git/RTD metadata, recursively includes source `.pyx`, `.pyi`, `.py`, `.pxi`, `.pxd`, `.c`, `.h`, and excludes `.pyc`.

Control flow: Packaging configuration only; consumed during sdist generation.

State and persistence: Affects package artifact contents.

Dependencies and integration: Integrates Python packaging with Cython/C headers and docs/test distribution.

Risks and test signals: Missing generated C/header files can break offline builds; over-including tests/docs increases sdist size. Validate with `python -m build --sdist` and inspect archive contents.
