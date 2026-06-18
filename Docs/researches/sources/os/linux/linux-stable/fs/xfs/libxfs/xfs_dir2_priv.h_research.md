# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_dir2_priv.h

## Purpose

`xfs_dir2_priv.h` is the private interface header tying together XFS directory v2/v3 implementation files. It declares shared in-core header abstractions, cross-file helpers for block/data/leaf/node/shortform directory formats, and common inline size calculations.

## Key Types

- `struct xfs_dir3_icleaf_hdr` is an in-core representation of v2/v3 leaf block headers. It decodes sibling pointers, magic, count, stale count, and points to on-disk leaf entries.
- `struct xfs_dir3_icfree_hdr` is an in-core representation of v2/v3 freespace block headers. It decodes magic, `firstdb`, `nvalid`, `nused`, and points to the on-disk `bests` array.

These abstractions let callers avoid duplicating v2/v3 layout conditionals.

## Declared Interface Groups

- `xfs_dir2.c`: case-insensitive hash/compare, inode growth, and CI lookup result helpers.
- `xfs_dir2_block.c`: block-format read/add/lookup/remove/replace and conversions.
- `xfs_dir2_data.c`: data-block bestfree, ftype/tag helpers, verification, read/readahead, free insertion, and initialization.
- `xfs_dir2_leaf.c`: leaf header conversion, read paths, block-to-leaf conversion, leaf add/lookup/remove/replace, leaf compaction/logging/searching/trimming, and node-to-leaf conversion.
- `xfs_dir2_node.c`: free header conversion, leaf-to-node conversion, leafn operations, node add/lookup/remove/replace, freespace trimming, and free-block reads.
- `xfs_dir2_sf.c`: shortform inode/parent/ftype helpers, block-to-shortform conversion, shortform add/create/lookup/remove/replace/verify, and local entry sizing.
- `xfs_dir2_readdir.c`: `xfs_readdir`.

## Inline Helpers

- `xfs_dir2_data_unusedsize` rounds unused-entry sizes to directory data alignment.
- `xfs_dir2_data_entsize` computes the aligned on-disk size of a data-block dirent from name length, including the trailing tag and optional filetype byte.

## Conditional Debug Interface

`xfs_dir3_data_check` is declared only for debug builds; non-debug builds compile it away. The stronger non-debug verifier entry point `__xfs_dir3_data_check` remains declared for buffer verification.

## Dependencies and Role

This header is intentionally private to XFS directory implementation code and scrub/repair users. It is not the public VFS-facing directory interface. It encodes the ownership boundaries among `xfs_dir2_block.c`, `xfs_dir2_data.c`, `xfs_dir2_leaf.c`, `xfs_dir2_node.c`, and `xfs_dir2_sf.c`.
