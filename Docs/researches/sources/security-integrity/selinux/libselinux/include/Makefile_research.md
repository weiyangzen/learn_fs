# sources/security-integrity/selinux/libselinux/include/Makefile

## Purpose
This makefile installs libselinux public headers into the target include directory.

## Important APIs, types, and functions
Key variables are `PREFIX ?= /usr` and `INCDIR = $(PREFIX)/include/selinux`. The `install` target creates `$(DESTDIR)$(INCDIR)` with mode 755 and installs `selinux/*.h` with mode 644. `all` and `relabel` are no-ops. `clean` and `distclean` remove editor backup files under `selinux/`.

## Control flow
Running `make install` first ensures the include directory exists, then copies every header matching the wildcard. Clean targets remove `selinux/*~` and ignore missing files.

## State and persistence behavior
Persistent effects are limited to installed header files under `DESTDIR` and cleanup of local backup files. The makefile does not generate headers.

## Dependencies and integration points
It is called by the top-level libselinux makefile and depends on POSIX `test`, `install`, and `rm`. It publishes headers such as `selinux.h`, `label.h`, `restorecon.h`, and `avc.h` for downstream C consumers.

## Risks and edge cases
If the wildcard expands to an empty list, install behavior is shell-dependent and may fail trying to copy a literal pattern. The install command does not remove stale headers already present in the destination. Directory ownership and SELinux labels are left to the packaging/install environment.

## Test signals
Tests should run `make install DESTDIR=...`, verify all expected headers and modes, check no-op `all` and `relabel`, and confirm `clean` removes only backup files.
