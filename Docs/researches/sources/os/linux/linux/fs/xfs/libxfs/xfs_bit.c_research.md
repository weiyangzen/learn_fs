# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_bit.c

## Purpose
Implements small bitmap scanning helpers used by XFS non-realtime code.

## Main Interfaces
- `xfs_bitmap_empty()` returns whether all words in a bitmap are zero.
- `xfs_contig_bits()` counts contiguous set bits starting at a given bit.
- `xfs_next_bit()` finds the next set bit at or after a start bit, or returns `-1`.

## Control Flow
`xfs_bitmap_empty()` linearly scans each word for nonzero content. `xfs_contig_bits()` advances to the starting word, masks bits before the requested start as already set, scans full words equal to `~0U`, and uses `ffz()` to find the first clear bit. `xfs_next_bit()` similarly advances to the starting word, masks off bits before the requested start, scans for a nonzero word, and uses `ffs()` to return the next set bit.

## State And Assumptions
Bitmap sizes are expressed in machine words, not bytes. Bit offsets are converted using `BIT_TO_WORD_SHIFT` and `NBWORD`. `xfs_contig_bits()` asserts that `start_bit` is inside the bitmap, while `xfs_next_bit()` returns `-1` if the start is outside.

## Integration Points
Declared by `xfs_bit.h` and used by XFS code that needs compact bitmap scans without open-coding word and bit arithmetic.

## Risks And Review Focus
- Callers must pass word counts, not byte counts.
- `xfs_contig_bits()` relies on the start bit being in range; unlike `xfs_next_bit()`, it asserts instead of gracefully returning.
- The functions operate on `uint` words and therefore depend on the platform word constants used by XFS.
