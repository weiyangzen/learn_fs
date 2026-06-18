# File Research: sources/os/bsd/freebsd-src/sbin/ping/tests/Makefile

ATF test build file for ping tests.

Key elements:
- Builds C ATF test `in_cksum_test` from `in_cksum_test.c` plus parent-directory `utils.c`.
- Registers pytest test `test_ping.py` and shell ATF test `ping_test`.
- Marks `ping_test` exclusive because injection cases reuse fixed IP addresses.
- Installs expected-output fixtures and `injection.py`.

Dependencies:
- Uses FreeBSD `bsd.test.mk`.
- Depends on parent `utils.c` for checksum test coverage.
