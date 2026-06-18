# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printtunable.c

IPFilter tunable formatter.

Key behavior:
- Prints name, min, max, and current value.
- Chooses current-value member based on `ipft_sz`.

Research notes:
- Unknown sizes are printed as `sz = n`.
