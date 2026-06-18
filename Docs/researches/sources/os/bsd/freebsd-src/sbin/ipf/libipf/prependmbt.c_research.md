# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/prependmbt.c

Mbuf-chain prepend helper for emulated packet handling.

Key behavior:
- Inserts `m` at the front of `*fin->fin_mp`.
- Returns zero unconditionally.

Research notes:
- No validation of `fin`, `fin_mp`, or `m`.
