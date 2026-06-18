# File Research: sources/local-fs/xfsprogs/libxfs/xfs_dir2_priv.h

## Purpose
Defines private interfaces and in-core helper structures for XFS dir2/dir3 directory implementation files.

## Main Contents
- `struct xfs_dir3_icleaf_hdr` and `struct xfs_dir3_icfree_hdr` provide v2/v3-neutral in-core views of leaf and free-block headers.
- Declares private helpers across `xfs_dir2.c`, block, data, leaf, node, shortform, and readdir implementations.
- Provides inline size helpers: `xfs_dir2_data_unusedsize()` and `xfs_dir2_data_entsize()`.
- Declares name hashing/comparison helpers `xfs_dir2_hashname()` and `xfs_dir2_compname()`.

## Integration
This header is the private contract tying together directory format variants: shortform, block, leaf, and node. The inline entry-size calculation centralizes ftype-aware dirent sizing, which is used throughout data-block mutation and verification code.

## Risks and Notes
Because this header exposes many cross-file private functions, changes to directory geometry, ftype storage, CRC-era layout, or shortform inode encoding must be coordinated across all declared implementations. The in-core header structs intentionally carry pointers into on-disk buffers, so callers must not outlive or move the underlying buffer.
