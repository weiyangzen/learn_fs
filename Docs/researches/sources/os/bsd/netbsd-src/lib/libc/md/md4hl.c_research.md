# File Research: sources/os/bsd/netbsd-src/lib/libc/md/md4hl.c

Read completely: 16 lines.

This file instantiates `mdXhl.c` for MD4 by defining `MDALGORITHM` as `MD4` and `MDINCLUDE` as `<md4.h>`.

Important interactions: produces high-level `MD4End`, `MD4File`, and `MD4Data` functions from the generic template.

Security/reliability notes: MD4 is obsolete and collision-prone. This wrapper contains no independent logic.
