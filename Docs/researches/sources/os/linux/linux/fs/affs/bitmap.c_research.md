# File Research: sources/os/linux/linux/fs/affs/bitmap.c

Implements AFFS bitmap-based free-space accounting, allocation, deallocation, initialization, and cleanup.

Key behavior:
- `affs_count_free_blocks()` sums cached per-bitmap free counts under `s_bmlock`; returns zero for read-only mounts.
- `affs_free_block()`:
  - Validates block range.
  - Locates the bitmap block and bit for the block.
  - Reads/caches the active bitmap buffer.
  - Detects double-free attempts.
  - Sets the free bit, adjusts bitmap checksum, marks buffer and superblock dirty, and increments free count.
- `affs_alloc_block()`:
  - Uses inode preallocation first when available.
  - Normalizes invalid goals to the reserved boundary.
  - Searches bitmap blocks with free space, wrapping as needed.
  - Locates a free bit in big-endian bitmap words.
  - Preallocates consecutive free bits within the same word.
  - Clears allocated bits, adjusts checksum, marks bitmap/superblock dirty, and returns the allocated block.
  - Returns zero on full filesystem or bitmap read failure.
- `affs_init_bitmap()`:
  - Skips initialization for read-only mounts.
  - Forces read-only if the root bitmap valid flag is clear.
  - Computes bitmap geometry and allocates `s_bitmap`.
  - Reads bitmap block pointers from the root block and bitmap extension blocks.
  - Validates bitmap checksums, forcing read-only on invalid bitmap.
  - Counts free bits with `memweight()`.
  - Marks unused bits beyond partition end allocated in the last bitmap block and recomputes its checksum.
- `affs_free_bitmap()` releases the cached bitmap buffer and bitmap info array.

Important interactions:
- Allocation/freeing are protected by `s_bmlock`.
- `affs_alloc_block()` maintains per-inode last allocation and preallocation state.
- Invalid bitmap state downgrades the mount to read-only rather than continuing writable operation.
