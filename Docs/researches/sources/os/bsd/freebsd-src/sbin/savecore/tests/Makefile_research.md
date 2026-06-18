# File Research: sources/os/bsd/freebsd-src/sbin/savecore/tests/Makefile

## Summary
Registers the `savecore` ATF shell tests.

## Main Elements
- Sets `ATF_TESTS_SH=livedump_test log_test`.
- Marks `livedump_test` exclusive because loading kernel modules during the test can change live-dump state.
- Includes `bsd.test.mk`.

## Dependencies And Integration
Integrates with FreeBSD ATF/Kyua test infrastructure.
