# File Research: sources/os/linux/linux/fs/xfs/scrub/bmap.c

This file scrubs inode fork block mappings for data, attr, and CoW forks. It validates fork format, bmbt structure, incore extent records, physical target ranges, logical ordering, and cross-references against rmap, free-space, inode, refcount/shared, CoW staging, and realtime metadata.

`xchk_setup_inode_bmap` obtains and locks the inode, drains intents when needed, serializes with IO and mmap activity for regular data/CoW fork checks, breaks layouts for repair, flushes dirty page-cache data, optionally invalidates page cache before repair, allocates a scrub transaction, attaches quotas, and takes `ILOCK_EXCL`.

The core scrub context `struct xchk_bmap_info` records the fork, previous mapping, incore extent cursor, realtime status, shared/reflink status, and whether the incore extent tree was already loaded. Btree-format forks are scrubbed by `xchk_bmap_btree`, which loads extents, runs the generic btree checker, verifies btree block owners for CRC filesystems, and compares btree records to the incore extent tree when appropriate.

The incore mapping pass coalesces adjacent logical and physical records where safe, including a guard against merging across realtime group boundaries. It detects holes in extent arrays, excessive record lengths, out-of-order mappings, invalid file offsets, invalid data or realtime block ranges, unwritten attr extents, and directory/attr offsets that cannot fit in `xfs_dablk_t`. Delalloc reservations are checked separately for file-range validity and max extent length.

Datadev and realtime xrefs verify that mapped space is allocated, not an inode chunk, has a matching rmap owner/offset/flags, is not incorrectly shared, and has correct CoW staging state. CoW fork rmaps are checked with owner `XFS_RMAP_OWN_COW` and no file offsets. For suspicious empty data or attr forks, the scrubber can scan all AG or realtime rmap btrees to find rmaps for the inode that lack matching bmap records, which detects fork-zap damage.

Entry points are `xchk_bmap_data`, `xchk_bmap_attr`, and `xchk_bmap_cow`. Data and attr variants also clear the corresponding zapped-health state when the fork validates cleanly.
