# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/Makefile

## Purpose
Builds pfctl regression tests.

## Main Elements
- Declares C ATF test `pfctl_test` and shell ATF test `macro`.
- Adds `files` subdirectory for test input/output data.
- Links `pfctl_test` with `libsbuf`.
- Makes `pfctl_test.o` depend on `pfctl_test_list.inc`.

## Dependencies And Integration
Included by FreeBSD test build infrastructure via `bsd.test.mk`.

## Risk Notes
The generated test set depends on the included list file; missing dependency updates can leave stale test cases.
