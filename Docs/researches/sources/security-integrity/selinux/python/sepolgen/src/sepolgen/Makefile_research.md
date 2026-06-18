# sources/security-integrity/selinux/python/sepolgen/src/sepolgen/Makefile

## Purpose
This makefile installs the Python `sepolgen` package files into the configured Python purelib directory and cleans generated artifacts.

## Important APIs, types, and functions
- Variables: `PREFIX ?= /usr`, `PYTHON ?= python3`, `PYTHONLIBDIR ?= $(shell $(PYTHON) -c ...)`, and `PACKAGEDIR ?= /$(PYTHONLIBDIR)/sepolgen`.
- `install` creates `$(DESTDIR)$(PACKAGEDIR)` and installs `*.py` with mode `644`.
- `clean` removes parser artifacts, editor backups, bytecode, and `__pycache__`.

## Control flow
`PYTHONLIBDIR` is computed with `sysconfig.get_path('purelib', vars={'platbase': PREFIX, 'base': PREFIX})`. `install` depends on `all`, then runs `mkdir` and `install`.

## State and persistence behavior
The install target writes Python source files to the destination package directory. `clean` deletes local generated state but does not remove installed files.

## Dependencies and integration points
It depends on Python's `sysconfig`, shell tools `mkdir`, `install`, and `rm`, and packaging variables `DESTDIR`, `PREFIX`, and `PYTHON`. Parent makefiles delegate to it.

## Risks and edge cases
`PACKAGEDIR` includes a leading slash before `$(PYTHONLIBDIR)`. Because `PYTHONLIBDIR` is normally absolute, this yields a double slash in paths such as `//usr/lib/...`, which is usually harmless but untidy. The install command copies every `*.py` in the directory and has no package manifest filtering.

## Test signals
No direct tests are defined. Installation can be smoke-tested by importing `sepolgen` from the target environment.
