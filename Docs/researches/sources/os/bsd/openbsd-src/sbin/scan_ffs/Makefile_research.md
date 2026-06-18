# File Research: sources/os/bsd/openbsd-src/sbin/scan_ffs/Makefile

This Makefile builds the OpenBSD `scan_ffs` utility.

Key settings:
- `PROG=scan_ffs`
- Links with `-lutil` through `LDADD` and `${LIBUTIL}` through `DPADD`.
- Installs `scan_ffs.8`.

Integration:
- `scan_ffs.c` uses `opendev()` from libutil.

Risk notes:
- Minimal build wrapper; no special local targets.
