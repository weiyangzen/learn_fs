<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/semanage/Makefile -->
# sources/security-integrity/selinux/python/semanage/Makefile

## Purpose
Installs the Python `semanage` command, `seobject.py` module, bash completion, man pages, and runs semanage tests.

## Important APIs, Types, And Functions
Defines `PYTHON`, `SBINDIR`, `MANDIR`, `PYTHONLIBDIR` via `sysconfig`, `PACKAGEDIR`, `BASHCOMPLETIONDIR`, `TARGETS=semanage`, and `BASHCOMPLETIONS=semanage-bash-completion.sh`. Targets are `all`, `install`, `test`, `clean`, and `relabel`.

## Control Flow
`all` depends on the `semanage` script. `install` creates man/sbin/package/completion directories, installs `semanage`, all `*.8` man pages and localized man pages, installs `seobject.py` into the Python purelib path, and installs completion as `semanage`. `test` runs `test-semanage.py -a`.

## State And Persistence
Install persists command scripts, Python modules, documentation, and completion. Tests may mutate their configured test environment depending on `test-semanage.py`.

## Dependencies And Integration Points
Depends on Python sysconfig path calculation and the semanage Python module consumers, especially `chcat` using `seobject`.

## Risks And Edge Cases
`PYTHONLIBDIR` is computed with `platbase`/`base` set to `PREFIX`, so cross-install layouts depend on Python's sysconfig scheme. Installing every `*.8` can pick up unintended files.

## Test Signals
Staged install path validation, import of installed `seobject`, `semanage --help`, completion install, and `make test`.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/semanage/Makefile -->
