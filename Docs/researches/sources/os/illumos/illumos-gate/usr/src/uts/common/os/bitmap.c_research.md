# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/bitmap.c

## Purpose

`bitmap.c` provides low-level operations on arbitrary-size bitmaps represented as arrays of `ulong_t`. Callers own range validation and bitmap sizing.

## Main Interfaces

Functions are `bt_availbit`, `bt_gethighbit`, `bt_range`, `odd_parity`, `bt_getlowbit`, and `bt_copy`.

## Behavior

`bt_availbit()` scans for the first zero bit up to `nbits`, first by word and then by bit. It returns the bit index or `-1`.

`bt_gethighbit()` walks downward from a word index until it finds a nonzero word, then returns the global index of the highest set bit.

`bt_range()` finds a consecutive run of set bits between `*pos1` and `end_pos`, returning the first set bit and one-past-last bit through `pos1` and `pos2`.

`odd_parity()` folds a `ulong_t` with shifts/xors until one parity bit remains.

`bt_getlowbit()` finds the lowest set bit in an inclusive `[start, stop]` range. It masks partial start and stop words and uses `lowbit()` on the first nonzero word.

`bt_copy()` copies a bitmap word array.

## Notable Invariants

- Bitmap size and range validity are caller responsibilities.
- `bt_availbit()` assumes `nbits > 0` because it subtracts one before computing the last word.
- Word-boundary masking in `bt_getlowbit()` is central to correctness for unaligned ranges.

## Dependencies

The file depends on bitmap macros from `sys/bitmap.h`, `highbit()`, `lowbit()`, and `ASSERT`.

## Research Notes

This is shared primitive code. Audit focus should be boundary handling for zero-sized inputs, inclusive stop ranges, and shift expressions around `partial_stop + 1`.
