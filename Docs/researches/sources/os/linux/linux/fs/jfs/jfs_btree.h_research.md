# File Research: sources/os/linux/linux/fs/jfs/jfs_btree.h

## Purpose
Provides common B+tree constants, macros, and traversal-stack structures shared by JFS directory trees and extent trees.

## Main Definitions
- Page flags: `BT_ROOT`, `BT_LEAF`, `BT_INTERNAL`, `BT_RIGHTMOST`, `BT_LEFTMOST`, and fsck-only `BT_SWAPPED`.
- Operation/order flags: random/sequential plus lookup/insert/delete markers.
- `BT_IS_ROOT()` distinguishes inline inode-root tree pages from metapage-backed pages.
- `BT_PAGE()`, `BT_GETPAGE()`, `BT_MARK_DIRTY()`, and `BT_PUTPAGE()` abstract root-vs-metapage access and dirtying.
- `struct btframe` records block number, entry index, last index, and metapage.
- `struct btstack` stores traversal frames up to `MAXTREEHEIGHT`.
- Stack macros initialize, push/pop, test full, and retrieve search results.

## Debug Support
- `BT_STACK_DUMP()` prints stack frame block numbers and indexes.

## Dependencies
- Uses JFS inode private data (`JFS_IP()`), metapages, `read_metapage()`, `mark_inode_dirty()`, `mark_metapage_dirty()`, and `jfs_err()`.

## Notable Behavior
- Root pages are stored inline in inode private data, using a fake metapage pointer based on `JFS_IP(IP)->bxflag`.
- Non-root pages are normal metapage buffers and must be released.
