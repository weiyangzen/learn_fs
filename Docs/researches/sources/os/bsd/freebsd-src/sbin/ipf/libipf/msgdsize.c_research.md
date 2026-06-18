# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/msgdsize.c

Message-chain byte counter.

Key behavior:
- `msgdsize()` walks an `mb_t` chain and sums `mb_len`.

Research notes:
- Used by packet printing assertions to compare logical IP length with mbuf-chain size.
