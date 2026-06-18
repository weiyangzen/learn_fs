# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_btree.h

Shared B+-tree definitions for JFS directory trees and extent trees.

Key content:
- Defines B-tree page flags: root, leaf, internal, rightmost, leftmost, swapped.
- Defines operation/order hints such as random/sequential lookup/insert/delete.
- Provides macros for root-vs-metapage access: `BT_IS_ROOT`, `BT_PAGE`, `BT_GETPAGE`, `BT_MARK_DIRTY`, and `BT_PUTPAGE`.
- Defines traversal stack structures `btframe` and `btstack`, plus push/pop/access macros.
- `BT_GETSEARCH` and `BT_PUTSEARCH` retrieve/release search-result pages.

Risk notes:
- Heavy macro use means callers must supply correct root field names and metapage variables.
- Root pages are embedded in inode memory, while non-root pages are metapages; dirty/release behavior differs by `BT_IS_ROOT()`.
