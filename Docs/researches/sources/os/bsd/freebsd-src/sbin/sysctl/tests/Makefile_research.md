# File Research: sources/os/bsd/freebsd-src/sbin/sysctl/tests/Makefile

## Purpose
Builds and installs the shell ATF tests for `sysctl`.

## Main Elements
- Defines `ATF_TESTS_SH=sysctl_test`.
- Includes `bsd.test.mk`.

## Dependencies And Integration
Participates in FreeBSD’s ATF/Kyua test infrastructure.

## Risk Notes
No conditional logic; all behavior is in `sysctl_test.sh`.
