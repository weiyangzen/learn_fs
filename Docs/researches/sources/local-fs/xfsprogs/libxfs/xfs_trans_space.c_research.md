# File Research: sources/local-fs/xfsprogs/libxfs/xfs_trans_space.c

This file computes filesystem block-space reservations for namespace operations. Unlike `xfs_trans_resv.c`, which sizes log space, these helpers estimate data/metadata blocks needed to complete operations.

`xfs_parent_calc_space_res` computes the block reservation required to add a parent pointer xattr: a DA entry reservation for the attr fork plus next-extent reservation for the parent name. The comment notes parent pointers are always the first attr in an attr tree and never larger than a block.

Create, mkdir, link, symlink, remove, and rename space reservations compose directory entry costs, inode allocation costs, symlink remote data blocks, and optional parent pointer xattr costs. `xfs_rename_space_res` handles standard rename, target replacement, and whiteout cases; with parent pointers it reserves for source/destination parent updates and extra whiteout parent creation.

These helpers depend on macros from `xfs_trans_space.h`, mount feature predicates, and mount geometry derived earlier. They are used by higher-level operation code to reserve enough filesystem blocks before starting transactional namespace changes.
