# File Research: sources/os/bsd/freebsd-src/sys/sys/_seqc.h

Sequence counter typedef.

Key elements:
- Defines `seqc_t` as `uint32_t`.

Dependencies:
- Assumes `uint32_t` is visible.

Research notes:
- Minimal public-domain shim for sequence counter users.
- Sequence counters are used for low-overhead consistency checks in concurrent kernel data paths.
