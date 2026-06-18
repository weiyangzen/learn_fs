# File Research: sources/local-fs/xfsprogs/libxfs/xfs_bit.h

## Purpose

`xfs_bit.h` declares XFS bitmap helpers and provides inline bit-mask and bit-position utilities.

## Key Contents

The mask helpers build high or low bit masks for 32-bit and 64-bit values. `xfs_highbit32` and `xfs_highbit64` return the highest set bit index or `-1` if the value is zero. `xfs_lowbit32` and `xfs_lowbit64` return the lowest set bit index or `-1` if none is set; the 64-bit low-bit helper checks the low word first and then the high word.

The header declares `xfs_bitmap_empty`, `xfs_contig_bits`, and `xfs_next_bit` from `xfs_bit.c`.

## Dependencies and Risks

The inline helpers depend on platform `fls`, `fls64`, and `ffs` semantics where zero returns 0. Mask helpers assume meaningful `n` values from callers; shifting by the full width or negative values would be invalid C behavior.
