# File Research: sources/os/bsd/freebsd-src/sbin/md5/tests/Makefile

## Purpose
Registers the md5 test script with the FreeBSD ATF test framework.

## Main Responsibilities
- Sets `PACKAGE=tests`.
- Adds shell ATF test `md5_test`.
- Includes `bsd.test.mk`.
