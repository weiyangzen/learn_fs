# sources/security-integrity/selinux/python/sepolgen/src/Makefile

## Purpose
This makefile coordinates installation and cleanup for sepolgen source components under `src`.

## Important APIs, types, and functions
Targets are `all`, `install`, `relabel`, `clean`, and `test`. `install` delegates to `sepolgen` and `share`. `clean` delegates to the same two subdirectories and removes local generated/parser/editor/bytecode files. `all`, `relabel`, and `test` are no-ops.

## Control flow
Make routes `install` or `clean` to child directories via `$(MAKE) -C sepolgen $@` and `$(MAKE) -C share $@`.

## State and persistence behavior
`install` writes through child makefiles. `clean` deletes local `*~`, `*.pyc`, `parser.out`, and `parsetab.py` after child cleanup.

## Dependencies and integration points
It requires `src/sepolgen/Makefile` and `src/share/Makefile`. It is invoked by the top-level sepolgen makefile and probably by package build scripts.

## Risks and edge cases
`test` is a no-op here, so top-level tests must come from `tests`, not `src`. The makefile assumes `share` exists and supports matching targets.

## Test signals
No direct tests are run from this makefile.
