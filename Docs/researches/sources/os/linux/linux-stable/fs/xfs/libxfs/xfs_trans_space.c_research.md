# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_trans_space.c

## Purpose

Computes filesystem block-space reservations for namespace operations, including parent pointer overhead.

## Main Functions

- `xfs_parent_calc_space_res`
  - Computes attr-fork space needed to add a parent pointer.
- `xfs_create_space_res`
  - Inode allocation plus directory entry insertion plus optional parent pointer.
- `xfs_mkdir_space_res`
  - Same as create.
- `xfs_link_space_res`
  - Directory entry insertion plus optional parent pointer.
- `xfs_symlink_space_res`
  - Inode allocation, directory entry insertion, remote symlink blocks, optional parent pointer.
- `xfs_remove_space_res`
  - Directory removal plus optional parent pointer removal.
- `xfs_rename_space_res`
  - Directory remove/enter costs plus parent pointer updates for target, whiteout, and existing target cases.

## Important Invariants

- Parent pointers are treated as attribute fork operations.
- Parent pointer attributes are assumed to be first in the attr tree and no larger than a block.
- Rename space is sensitive to whether the target exists and whether a whiteout is involved.

## Research Notes

This file complements log reservation sizing with block reservation sizing. Parent pointers are the main feature-dependent adjustment.
