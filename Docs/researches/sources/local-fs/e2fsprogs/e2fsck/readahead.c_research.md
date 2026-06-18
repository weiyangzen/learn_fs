# File Research: sources/local-fs/e2fsprogs/e2fsck/readahead.c

This file implements metadata prefetch helpers used to reduce e2fsck runtime.

Directory block readahead:
- `e2fsck_readahead_dblist(fs, flags, dblist, start, count)` iterates a directory block list and coalesces contiguous physical runs.
- `readahead_dir_block()` accumulates runs and issues `io_channel_cache_readahead()` when a run breaks.
- `E2FSCK_RA_DBLIST_IGNORE_BLOCKCNT` treats each dir block entry as one block regardless of `blockcnt`.

Bitmap-driven readahead:
- `e2fsck_readahead(fs, flags, start, ngroups)` builds a temporary block bitmap of metadata blocks to prefetch, then sends contiguous set-bit ranges to the io channel.
- It can mark superblocks, group descriptor tables, block bitmaps, inode bitmaps, and inode table ranges.
- It skips uninitialized or fully unused bitmap/table groups where appropriate.
- Helper functions `mark_bmap()` and `mark_bmap_range()` avoid range-error noise by bounds-checking before marking.

Capability and sizing:
- `e2fsck_can_readahead(fs)` probes support by attempting a one-block readahead.
- `e2fsck_guess_readahead(fs)` estimates a useful readahead window as two inode-table groups, but disables it if that would exceed 1/50 of memory.

Integration points:
- Called by pass 4 to prefetch bitmaps before pass 5.
- Uses ext2fs group-location and bitmap APIs plus io-channel cache readahead support.

Risk notes:
- Readahead failures propagate as errcodes but do not themselves repair metadata.
- The temporary bitmap bounds checks intentionally trade completeness for quiet failure on unexpected geometry.
