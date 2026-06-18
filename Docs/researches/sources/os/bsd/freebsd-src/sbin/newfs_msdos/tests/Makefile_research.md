# File Research: sources/os/bsd/freebsd-src/sbin/newfs_msdos/tests/Makefile

Connects FreeBSD `newfs_msdos` tests to imported NetBSD ATF shell tests.

Key contents:
- `TESTSRC=${SRCTOP}/contrib/netbsd-tests/sbin/newfs_msdos`.
- Adds `create` as a NetBSD ATF shell test.
- Applies sed substitution from `fsck_msdos` to FreeBSD `fsck_msdosfs`.
- Includes `netbsd-tests.test.mk` and `bsd.test.mk`.

Research notes:
- Test coverage is imported/adapted rather than local C tests.
