# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/util.c

Contains small host utility functions.

Key functions:
- `cvttorunes` converts UTF-8 bytes to `Rune` data, reporting consumed bytes, produced runes, and optional NUL count.
- `fbufalloc` and `fbuffree` allocate/free fixed-size file buffer memory.
- `min` returns the smaller of two unsigned integers.

Behavior notes:
- `cvttorunes` assumes the input byte count ends on a complete rune boundary.
- NUL runes are skipped from output but counted when `nulls` is provided.
