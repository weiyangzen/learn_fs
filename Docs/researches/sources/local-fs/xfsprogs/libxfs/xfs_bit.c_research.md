# File Research: sources/local-fs/xfsprogs/libxfs/xfs_bit.c

## Purpose

`xfs_bit.c` implements small bitmap scanning helpers used by non-realtime XFS code.

## Main APIs

`xfs_bitmap_empty` scans a word array and returns 1 if every word is zero. `xfs_contig_bits` counts contiguous one bits starting at a given bit position, masking off bits before the start position and using `ffz` to find the first zero. `xfs_next_bit` finds the next set bit at or after a start position, masking off prior bits and using `ffs` to locate the set bit.

## Dependencies and Risks

The file depends on word-size constants and bit primitives from platform headers and `xfs_bit.h`. The `size` argument is a count of bitmap words, not bytes; callers must pass a valid `start_bit` for `xfs_contig_bits`, which asserts that the start is within range.
