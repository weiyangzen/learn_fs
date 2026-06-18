# File Research: sources/local-fs/jfsutils/fsck/fsckxtre.c

## Purpose
Validates, searches, initializes, and accounts for JFS xtrees, the B+ tree format used for file data extents and some inode-rooted metadata. It connects tree structural validation with fsck’s block ownership and inode repair flags.

## Key Elements
`find_first_leaf()` descends from an inode’s xtree root to locate the leftmost leaf node, returning whether the data is root-leaf or inline/no-data. `init_xtree_root()` resets an inode’s xtree root to an empty root leaf and clears `di_nblocks`/`di_size`.

`process_valid_data()` walks an already validated xtree by level and sibling chain, calling `process_extent()` on each XAD and updating aggregate/inode block accounting. It supports record, unrecord, and query modes.

`xTree_processing()` is the main validator. It validates root header fields, normalizes fileset-inode-map action variants, detects dense-file front gaps, processes root leaf/internal nodes, then uses the `treeQ_*` queue from `fsckwsp.c` for breadth-first traversal of child nodes. It checks node level transitions, sibling forward/backward links, `header.self` against the parent XAD PXD, empty non-root nodes, valid leaf/internal flags, and consistency of corruption detection across later passes.

`xTree_process_internal_extents()` validates internal-node XAD flags and ascending keys, records each child-node extent through `process_extent()`, updates non-data block counts, and enqueues child nodes with their expected address, length, level, and first key.

`xTree_process_leaf_extents()` validates leaf XAD flags, ascending keys, dense-file gaps, odd-sized extents, and records/unrecords/query-checks data extents. It updates `this_inode.data_size`, `all_blks`, `data_blks`, and fileset block counts. Odd-sized extents are allowed only as the last possible extent, except for the bad-block inode.

`xTree_search()` descends the xtree to find a leaf XAD covering a requested file offset. It uses `xTree_binsrch_page()` to select the nearest XAD in each page and then either descends or checks whether the selected leaf extent covers the key.

## Dependencies
Depends on `xfsckint.h` xtree/XAD/PXD types and macros, `jfs_byteorder.h`, global `sb_ptr` and `agg_recptr`, `node_get()`, `treeQ_*` workspace queue routines, `process_extent()`, and fsck message helpers.

## Behavior/Risks
The validator is intentionally fail-fast: once structural corruption is detected, it sets `inorecptr->ignore_alloc_blks` and stops processing further allocations for that tree. Repair decisions elsewhere use this flag to release an inode, skip suspect allocation accounting, or keep later passes consistent.

Dense files are required to have contiguous leaf offsets, while sparse files only require strictly increasing non-overlapping keys. The code treats directory data roots specially by using `di_dirtable`; other inodes use `di_btroot`.

Fileset inode-map xtrees use special action aliases and skip leaf extent processing for that metadata tree, while still validating internal node storage. This distinction is important because callers can request FSIM-specific record/unrecord/query operations.

The traversal assumes the queue and node buffers are globally shared workspace resources. Corruption paths clean up pending queue elements before returning, but the code relies on `treeQ_back/front` being reset correctly between validations.
