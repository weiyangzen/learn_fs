# File Research: sources/os/bsd/freebsd-src/sbin/devd/tests/Makefile

## Purpose
Builds ATF tests for `devd` client sockets.

## Main Elements
- `ATF_TESTS_C=client_test`
- Requires `/var/run/devd.pid`, `devd`, root user, and 15-second timeout.
- `WARNS?=5`
- Includes `<bsd.test.mk>`.
