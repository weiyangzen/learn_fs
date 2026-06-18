# File Research: sources/os/linux/linux/fs/hfs/bitmap.c

## Scope

This file implements allocation and free operations for the HFS volume bitmap.

## Public And Internal APIs Covered

- Internal `hfs_find_set_zero_bits()` searches the big-endian bitmap for zero bits and sets the contiguous run it finds.
- `hfs_vbm_search_free()` allocates allocation blocks from the volume bitmap.
- `hfs_clear_vbm_bits()` frees allocation blocks in the volume bitmap.

## Control Flow And Behavior

`hfs_find_set_zero_bits()` starts from an offset, scans big-endian 32-bit words for the first clear bit in HFS left-to-right bit order, then sets bits up to the requested maximum or until it encounters an already-set bit. It updates `*max` to the number of bits actually set and returns the starting bit, or a value at/above size when no zero bit is found.

`hfs_vbm_search_free()` rejects zero-length requests, locks `bitmap_lock`, searches from the supplied goal to the end of the filesystem allocation-block range, wraps to zero if needed, and returns zero length/start when full. On success it decrements `free_ablocks`, marks the bitmap dirty, unlocks, and returns the starting allocation block.

`hfs_clear_vbm_bits()` validates nonzero work and range bounds, locks the bitmap, clears partial leading bits, full 32-bit words, and trailing bits, increments `free_ablocks`, unlocks, and marks the bitmap dirty.

## Dependencies

The file depends on `HFS_SB(sb)->bitmap`, `bitmap_lock`, `fs_ablocks`, `free_ablocks`, `hfs_bitmap_dirty()`, and big-endian bitmap storage.

## Risks And Invariants

The allocation helper both finds and sets bits; callers must hold/expect bitmap mutation. Its comments note it may read beyond the logical bit count within aligned memory. `hfs_clear_vbm_bits()` does not verify that bits were previously set despite historical comments mentioning already-clear detection; it simply clears and increments free count, so callers must not double-free ranges. Bitmap dirtying is required after every successful mutation.
