# sources/security-integrity/selinux/python/sepolgen/Makefile

## Purpose
This top-level sepolgen makefile delegates build lifecycle targets to subdirectories. It is a thin coordinator for the `src` and `tests` trees.

## Important APIs, types, and functions
Targets are `all`, `install`, `relabel`, `clean`, and `test`. `all` and `relabel` are no-ops. `install` delegates to `src`. `clean` delegates to `src` and `tests`, then removes local editor, bytecode, and parser generated files. `test` delegates to `tests`.

## Control flow
Make invokes the named target. Delegated targets use `$(MAKE) -C <dir> $@`, preserving the original target name.

## State and persistence behavior
`install` persists files only through the `src` sub-make. `clean` removes `*~`, `*.pyc`, `parser.out`, and `parsetab.py` in this directory after cleaning child directories.

## Dependencies and integration points
It depends on GNU/POSIX make semantics, `src/Makefile`, and `tests/Makefile`. The target names must match subdirectory makefiles.

## Risks and edge cases
There is no default build work in `all`, so packaging must know install is the meaningful target. If `tests/Makefile` is missing, `make clean` and `make test` fail even though source installation might be usable.

## Test signals
`make test` is the only test signal and is delegated entirely to `tests`.
