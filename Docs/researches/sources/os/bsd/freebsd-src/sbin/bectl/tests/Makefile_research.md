# File Research: sources/os/bsd/freebsd-src/sbin/bectl/tests/Makefile

## Purpose
Registers shell ATF tests for `bectl`.

## Main Elements
- Sets `PACKAGE=tests`.
- Adds `bectl_test` to `ATF_TESTS_SH`.
- Includes `bsd.test.mk`.

## Dependencies And Integration
Installs/runs `bectl_test.sh` through the FreeBSD ATF test framework.

## Risk Notes
No logic beyond test registration.
