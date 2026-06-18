# File Research: sources/local-fs/xfsprogs/libxfs/xfs_da_btree.h

## Purpose

`xfs_da_btree.h` declares the shared data structures and APIs for XFS directory and attribute B-tree operations.

## Key Contents

The header defines `struct xfs_da_geometry`, which captures block size, filesystem block count, log shifts, node/leaf/free block geometry, dir section block numbers, max extents, and data-entry offsets for both directory and attribute forks.

`struct xfs_da_args` is the central operation context for directory and xattr operations. It carries names, values, inode/transaction pointers, owner, inode number, file type, operation flags, attr namespace filters, hashes, reservation totals, fork selector, current block/index state, remote attr value state, secondary attr replace state, and comparison result.

The state structures `xfs_da_state_blk`, `xfs_da_state_path`, and `xfs_da_state` track the active descent path, alternate path for joins, split target information, and extra split blocks. `struct xfs_da3_icnode_hdr` is the in-core abstraction for legacy and CRC-enabled da node headers.

The exported APIs cover node creation, split/join, hash-path repair, node lookup/path shifting, sibling linking, node reads, inode grow/shrink, buffer get/read/readahead, buffer copy, name hashing/comparison, state allocation/reset/free, header conversion, and header verification.

## Dependencies and Risks

Callers must initialize `xfs_da_args` consistently with mount geometry, fork type, owner, transaction, and operation flags. The main invariants are correct path depth tracking, hash ordering, block ownership, and preserving the distinction between directory data fork geometry and attribute fork geometry.
