# File Research: sources/os/bsd/dragonflybsd/sys/sys/copyright.h

Kernel copyright string aggregation header.

Key responsibilities:
- Defines string macros for DragonFly, FreeBSD, and UCB copyright notices.
- Defines global `char copyright[]` concatenating DragonFly, FreeBSD, and UCB notices.
- DragonFly string covers 2003-2026 in this tree.

Dependencies:
- None beyond C string literal concatenation.

Notable risks:
- This header defines storage, not just declarations; including it from multiple translation units would create duplicate definitions unless used carefully.
