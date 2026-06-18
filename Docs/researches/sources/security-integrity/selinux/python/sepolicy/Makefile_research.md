# sources/security-integrity/selinux/python/sepolicy/Makefile

## Purpose
This Makefile builds, tests, and installs the `sepolicy` Python command package and CLI wrapper. It also installs man pages and bash completion, and creates the compatibility `sepolgen` symlink.

## Important Targets And Variables
`PYTHON ?= python3`, `PREFIX ?= /usr`, `BINDIR`, `MANDIR`, and `BASHCOMPLETIONDIR` define build/install paths. `python-build` runs `$(PYTHON) -m build --no-isolation --wheel .`. `install` builds a wheel, force-reinstalls it with pip under `$(PREFIX)` and optional `DESTDIR`, installs `sepolicy.py` as `$(BINDIR)/sepolicy`, creates `sepolgen -> sepolicy`, installs man pages including localized `$(LINGUAS)` subdirectories, and installs completion as `sepolicy`.

`clean` removes Python build outputs, egg metadata, backups, and bytecode. `test` runs `test_sepolicy.py -v`. `sepolgen` creates only the symlink in the current directory. `relabel` is an empty placeholder.

## Control Flow
Build flow is wheel-based. Install flow combines Python packaging with manual CLI/man/completion installation. The pip command conditionally emits `--root $(DESTDIR) --ignore-installed --no-deps` only when `DESTDIR` is non-empty.

## State And Persistence
Persistent outputs include `build/`, `dist/`, egg-info during build, installed Python package files, `/usr/bin/sepolicy` by default, a `sepolgen` symlink, man pages, and bash completion. Local `clean` removes build state but not installed state.

## Dependencies And Integration Points
It depends on Python build tooling, pip, wheel metadata in the directory, man page files matching `*.8`, optional localized man page directories, and `sepolicy-bash-completion.sh`. The installed CLI wrapper executes `sepolicy.py`.

## Risks And Edge Cases
`CFLAGS` is set and extended but this Makefile path is mostly Python packaging; its relevance depends on package build internals. The `install` rule force-reinstalls from `dist/*.whl`, which can be ambiguous if multiple wheels remain. There is no uninstall target. The symlink name means invoking the same script as `sepolgen` changes default CLI behavior in `sepolicy.py`.

## Test Signals
The only test target runs `test_sepolicy.py`, not included in this subset. Successful installation should be validated by command execution, man page presence, and completion loading.
