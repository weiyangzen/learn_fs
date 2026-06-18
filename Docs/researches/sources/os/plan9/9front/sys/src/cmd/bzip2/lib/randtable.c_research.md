# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/randtable.c

Purpose: Defines the 512-entry randomization table used for old bzip2 randomized blocks.

Key points:
- `BZ2_rNums[512]` is static integer data.
- Compression no longer emits randomized blocks, but decompression still supports them for backward compatibility.

Dependencies and interactions:
- Randomization macros in `bzlib_private.h` reference this table.
- `decompress.c` uses the randomization mask path when a block’s randomization bit is set.

Research notes:
- Static compatibility data. Exact values must be preserved.
