# File Research: sources/os/linux/linux-stable/fs/affs/bitmap.c

This file owns AFFS bitmap loading, free-space counting, block allocation, block freeing, and bitmap teardown.

Major responsibilities:
- Counts free blocks by summing per-bitmap `bm_free` counters under `s_bmlock`.
- Frees a block by locating its bitmap block, setting the target bit, adjusting the bitmap checksum, marking the bitmap dirty, and incrementing `bm_free`.
- Allocates a block near a goal, scanning bitmap blocks for a set bit, clearing it, fixing the checksum, updating `bm_free`, and returning the physical block number.
- Maintains a cached current bitmap buffer in `s_bmap_bh`/`s_last_bmap` to reduce repeated reads.
- Implements small preallocation by reserving additional free bits in the same 32-bit bitmap word and recording them in the inode’s `i_pa_cnt`/`i_lastalloc`.
- Initializes bitmap state during mount and releases it during unmount or read-only remount.

Bitmap format and accounting:
- Bitmap bit value `1` means free and `0` means allocated.
- Each bitmap block reserves the first 32 bits for checksum storage, so `s_bmap_bits = blocksize * 8 - 32`.
- `affs_init_bitmap()` walks bitmap pointers from the root block and bitmap extension blocks, validates checksums, and calculates free counts with `memweight()`.
- The last bitmap block is corrected so bits beyond the partition end are forced allocated, then the checksum is recomputed.

Error handling:
- Invalid frees outside the partition are reported as AFFS errors.
- Double-free attempts are detected by testing whether the bit is already set.
- Bitmap read failures clear the cached bitmap buffer and return gracefully for free or allocation paths.
- Invalid bitmap checksums cause the filesystem to be mounted read-only rather than trusted for writes.

Concurrency:
- All bitmap mutation and cached bitmap buffer changes are serialized by `s_bmlock`.
- The allocation path updates both the in-memory counter and on-disk bitmap/checksum while the lock is held.
