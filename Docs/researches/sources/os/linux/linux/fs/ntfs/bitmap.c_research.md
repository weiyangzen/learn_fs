# File Research: sources/os/linux/linux/fs/ntfs/bitmap.c

Implements NTFS bitmap mutation and filesystem trim support.

Key entry points:
- `ntfs_trim_fs()` scans the volume LCN bitmap for free clusters and issues discard requests.
- `__ntfs_bitmap_set_bits_in_run()` sets or clears a bit range in a bitmap inode with rollback support.

Core mechanics:
- `ntfs_trim_fs()` converts the requested byte range to cluster bounds, reads bitmap folios, finds zero-bit runs, aligns discards to block-device discard granularity or cluster size, and accumulates the trimmed byte count in `range->len`.
- Bitmap scan windows are page-sized: one page represents `PAGE_SIZE * 8` clusters.
- `__ntfs_bitmap_set_bits_in_run()` maps bitmap folios, handles partial first byte, whole bytes, subsequent pages, and partial final byte.
- When mutating the volume `$Bitmap` (`FILE_Bitmap`), it updates in-memory empty-bit accounting via `ntfs_set_lcn_empty_bits()`.
- On a subsequent-page mapping failure after partial modification, it recursively rolls back the modified prefix by writing the opposite bit value.

Important invariants:
- Bit ranges must have non-negative start/count and value must be 0 or 1.
- Folios are locked, locally mapped, modified, marked dirty, unlocked, and released.
- Rollback mode suppresses another rollback attempt and returns the original error.

Notable risks:
- Trim alignment uses aligned byte ranges inside cluster runs; small or misaligned free runs below `range->minlen` are skipped.
- If rollback fails after a bitmap mutation error, the volume is marked erroneous and metadata may be inconsistent.
