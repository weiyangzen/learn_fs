# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/tests/pfctl_test_list.inc

## Purpose
Single source of truth for pfctl ATF test registration.

## Main Elements
- Lists OpenBSD-derived tests `0001` through `0104`.
- Lists FreeBSD-specific tests `1001` through `1079`.
- Marks expected-failure tests with `PFCTL_TEST_FAIL`.
- Marks interface/vnet-dependent tests with `PFCTL_TEST_IFACE`.
- Intentionally has no include guards because it is included multiple times with different macro definitions.

## Dependencies And Integration
Included by `pfctl_test.c` to generate ATF test case declarations, bodies, and registrations.

## Risk Notes
Adding or renaming test data requires updating this file consistently with corresponding `.in`, `.ok`, and optional `.fail` files.
