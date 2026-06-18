# File Research: sources/os/bsd/dragonflybsd/sys/sys/dkstat.h

Kernel-only legacy disk/tape statistics extern header.

Key responsibilities:
- Declares global counters `tk_nin`, `tk_nout`, and `tk_rawcc`.

Dependencies:
- Kernel/kernel-structures only; includes `sys/types.h`.

Notable risks:
- Header errors if included from normal userland.
- These are global counters, so users need to know where accounting is updated and synchronized.
