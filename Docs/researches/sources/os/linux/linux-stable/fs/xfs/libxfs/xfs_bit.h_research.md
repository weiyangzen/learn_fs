# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_bit.h

## Purpose

`xfs_bit.h` declares and defines XFS bit manipulation helpers used by bitmap and extent-related code.

## Inline Helpers

- `xfs_mask64hi` creates a 64-bit mask with the top `n` bits set.
- `xfs_mask32lo` and `xfs_mask64lo` create low-bit masks.
- `xfs_highbit32` and `xfs_highbit64` return the index of the highest set bit or `-1` if none are set.
- `xfs_lowbit32` and `xfs_lowbit64` return the index of the lowest set bit or `-1` if none are set. The 64-bit low-bit helper checks the low 32 bits first, then the high 32 bits.

## External Functions

The header declares `xfs_bitmap_empty`, `xfs_contig_bits`, and `xfs_next_bit`, implemented in `xfs_bit.c`.

## Invariants and Risks

The mask helpers assume callers pass meaningful bit counts for the underlying shift width. Passing zero to the low-mask helpers would shift by zero and subtract one, producing zero as expected, but passing values outside the integer width would be invalid C shift behavior. Callers are expected to keep `n` within 0..32 or 0..64 as appropriate.
