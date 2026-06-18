# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_bit.c

## Purpose

`xfs_bit.c` implements simple bitmap scanning helpers used by non-realtime XFS code. The helpers operate on arrays of unsigned integer words and use XFS bit/word constants from `xfs_log_format.h` and `xfs_bit.h`.

## APIs

- `xfs_bitmap_empty` returns 1 if all words in the bitmap are zero, otherwise 0.
- `xfs_contig_bits` counts continuous set bits starting at a given bit. It masks off bits before the starting offset in the first word, then scans whole words looking for the first zero bit with `ffz`.
- `xfs_next_bit` returns the next set bit at or after `start_bit`, or `-1` if none exists or `start_bit` is beyond the bitmap. It masks off earlier bits in the first word and scans with `ffs`.

## Invariants and Edge Cases

`size` is measured in words, not bytes or bits. Both scanning helpers convert it to bits with `BIT_TO_WORD_SHIFT`. `xfs_contig_bits` asserts `start_bit < size_in_bits`; `xfs_next_bit` handles out-of-range starts by returning `-1`.

## Dependencies

The implementation relies on word size constants (`NBWORD`, `BIT_TO_WORD_SHIFT`) and low-level bit operations (`ffs`, `ffz`). It is intentionally small and does not allocate memory or touch filesystem state.
