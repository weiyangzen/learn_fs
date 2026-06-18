# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printtqtable.c

TCP state timeout-queue count printer.

Key behavior:
- Prints state indexes from `0` to `IPF_TCP_NSTATES - 1`.
- Prints `ifq_ref - 1` for each queue.

Research notes:
- The subtraction implies one internal reference is not counted as an entry.
