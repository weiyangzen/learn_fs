# sources/security-integrity/selinux/python/sepolgen/src/sepolgen/__init__.py

## Purpose
This is an empty package initializer for `sepolgen`. Its presence marks the directory as an importable Python package in Python versions and packaging contexts that still require `__init__.py`.

## Important APIs, types, and functions
It defines no public names, functions, classes, or side effects.

## Control flow
No code executes when imported beyond normal module initialization.

## State and persistence behavior
No state is stored or persisted.

## Dependencies and integration points
Other modules import this package namespace, such as `sepolgen.access`, `sepolgen.audit`, `sepolgen.defaults`, and `sepolgen.interfaces`. The makefile installs it with other `*.py` files.

## Risks and edge cases
The empty initializer intentionally does not expose convenience imports. Code must import concrete submodules directly.

## Test signals
A package import smoke test is sufficient: `import sepolgen` should succeed when the package path is installed.
