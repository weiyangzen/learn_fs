# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/tests/Makefile

Purpose: Build glue for `nvmecontrol` ATF tests.

Key behavior:
- Assigns tests to `PACKAGE=tests`.
- Registers `basic` as an ATF shell test.
- Includes `<bsd.test.mk>`.

Dependencies:
- FreeBSD bsd.test.mk infrastructure.

Research notes:
- Minimal Makefile; all test behavior is in `basic.sh`.
