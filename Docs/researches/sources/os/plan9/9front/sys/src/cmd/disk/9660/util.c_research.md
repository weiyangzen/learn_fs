# File Research: sources/os/plan9/9front/sys/src/cmd/disk/9660/util.c

Utility support for the ISO 9660 tools.

Key behavior:
- Implements an atom table for interned strings using 1024 hash buckets.
- Provides zeroing `emalloc`, fatal `erealloc`, uppercase-copy helper `struprcpy`, and conditional diagnostic printer `chat`.

Research notes:
- Atomized strings enable pointer comparisons in conform-map code.
- `erealloc` loses the old pointer in the error message expression after `realloc` assignment, but fatal exit makes recovery irrelevant.
