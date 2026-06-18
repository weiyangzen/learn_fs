# sources/security-integrity/selinux/python/sepolgen/src/share/Makefile

## Purpose
This Makefile installs sepolgen shared data, specifically `perm_map`, into the configured data directory. The data is consumed by the object model permission mapping tests and by sepolgen runtime components that need permission direction and weight metadata.

## Important Targets And Variables
`SHAREDIR ?= /var/lib/sepolgen` controls the install location. `all` is a no-op placeholder. `install` creates `$(DESTDIR)$(SHAREDIR)` and installs `perm_map` with mode `644`. `clean` removes editor backup files matching `*~`.

## Control Flow
The install path is standard make flow: `install` depends on `all`, ensures the destination directory exists, then copies `perm_map`. There is no build-time generation.

## State And Persistence
The only persistent artifact is the installed `perm_map` file under the share directory. `DESTDIR` supports packaging roots without changing the final logical `SHAREDIR`.

## Dependencies And Integration Points
It depends on shell tools `mkdir` and `install`, and on the source-side `perm_map` file. `tests/test_objectmodel.py` opens `perm_map` locally during tests, while installed consumers normally expect `/var/lib/sepolgen/perm_map`.

## Risks And Edge Cases
The `-mkdir` prefix ignores directory creation failures, which may hide install problems until `install` fails. The Makefile does not install any other share data and assumes `perm_map` exists in the current working directory. There is no uninstall target.

## Test Signals
No direct Makefile test exists. The object-model test validates the semantics of a readable `perm_map` fixture by checking `filesystem mount` and default permission behavior.
