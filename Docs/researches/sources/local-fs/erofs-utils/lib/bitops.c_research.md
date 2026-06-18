# File Research: sources/local-fs/erofs-utils/lib/bitops.c

## Purpose
Provides a userspace implementation of a bit-scan helper used by EROFS buffer/cache logic.

## Important Functions
- `erofs_find_next_bit()`: finds the next set bit in an `unsigned long` bitmap starting at `start`, bounded by `nbits`.

## Behavior
- Returns `nbits` if `start >= nbits` or no bit is found.
- Masks bits before `start` in the first word.
- Advances by `BITS_PER_LONG` until a nonzero word is found.

## Interactions
- Used by `cache.c` bucket bitmap scanning.
- Depends on `erofs/bitops.h`.

## Notes
This mirrors kernel-style bitmap search semantics in a small userspace helper.
