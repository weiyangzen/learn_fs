# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/files/Makefile

## Purpose
Installs pfctl regression input, expected-output, include, and failure files.

## Main Elements
- Sets `TESTSDIR` and `BINDIR` under `${TESTSBASE}/sbin/pfctl/files`.
- Uses globbed `FILES!=` expansion for `pf????.in`, `.include`, `.ok`, and `.fail`.
- Includes `bsd.progs.mk`.

## Dependencies And Integration
Provides data files consumed by `pfctl_test.c`.

## Risk Notes
Glob expansion is tied to `${.CURDIR}` and four-digit naming; irregular filenames will not install.
