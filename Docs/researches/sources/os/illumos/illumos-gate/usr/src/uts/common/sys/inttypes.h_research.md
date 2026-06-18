# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/inttypes.h

This is the illumos kernel/driver-facing wrapper for C99 integer facilities.

Key behavior:
- Includes `sys/feature_tests.h` and `sys/int_types.h`.
- Includes `sys/int_limits.h`, `sys/int_const.h`, and `sys/int_fmtio.h` unless constrained by XOPEN namespace rules.
- Comment directs kernel/driver developers to include this file, while applications should use standard `<inttypes.h>`.

Relevance:
- Aggregates fixed-width integer types, limits, constants, and format macros for kernel and driver code.
