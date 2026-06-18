# File Research: sources/local-fs/btrfs-progs/kernel-lib/bitmap.h

## Purpose
Userspace wrapper for a small subset of Linux bitmap helpers used by btrfs-progs.

## Key Interfaces
- `bitmap_zalloc(nbits)` allocates zeroed storage sized by `BITS_TO_LONGS(nbits)`.
- `bitmap_free(bitmap)` frees bitmap storage.
- `bitmap_weight(bitmap, nbits)` returns the number of set bits in a bitmap.

## Dependencies
Includes `kerncompat.h`, `<stdlib.h>`, and `kernel-lib/bitops.h`.

## Risks And Review Notes
- `bitmap_zalloc()` calls `calloc(BITS_TO_LONGS(nbits), BITS_PER_LONG)`. Since `BITS_PER_LONG` is a bit count, not bytes, this overallocates by a factor of 8 on typical platforms. It is wasteful but usually safe.
- `bitmap_weight()` handles the trailing partial word as `ret += bitmap[i] & BITMAP_LAST_WORD_MASK(nbits)` rather than applying `hweight_long()` to the masked value. That overcounts whenever the masked low bits form a numeric value greater than their popcount.
- Macro typo `BITMAP_LAST_WORK_MASK` is defined but unused; the function uses `BITMAP_LAST_WORD_MASK` from `bitops.h`.
