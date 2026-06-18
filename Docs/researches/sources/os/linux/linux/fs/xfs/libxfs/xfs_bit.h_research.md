# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_bit.h

## Purpose
Declares XFS bit manipulation helpers and provides inline mask and high/low-bit routines.

## Main Interfaces
- Masks: `xfs_mask64hi()`, `xfs_mask32lo()`, `xfs_mask64lo()`.
- High bit: `xfs_highbit32()`, `xfs_highbit64()`.
- Low bit: `xfs_lowbit32()`, `xfs_lowbit64()`.
- Bitmap scans: `xfs_bitmap_empty()`, `xfs_contig_bits()`, `xfs_next_bit()`.

## Main Contents
The high-bit helpers wrap `fls()` and `fls64()` and return `-1` when no bit is set. The low-bit helpers wrap `ffs()` behavior; `xfs_lowbit64()` explicitly checks the lower 32 bits first and then the upper 32 bits, adding 32 when the low set bit is in the high half.

## Integration Points
Included by `xfs_bit.c` and other XFS code needing common mask or bit-index helpers. It relies on kernel bit primitives such as `fls`, `fls64`, `ffs`, and constants such as `NBWORD`.

## Risks And Review Focus
- The mask helpers assume valid `n` ranges; shifting by the type width would be undefined, so callers must avoid invalid counts.
- Return values use XFS’s historical “bit index or `-1`” convention rather than kernel bitops’ one-based `ffs` convention.
