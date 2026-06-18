# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_trans_space.c

## Purpose

`xfs_trans_space.c` computes filesystem block reservation counts for namespace operations. These are block-space reservations, distinct from log-space reservations in `xfs_trans_resv.c`.

## Main Content

- Computes parent pointer space reservation:
  - Parent pointer attr tree entry.
  - Additional attr fork extent mapping space.
- Computes create and mkdir space reservations:
  - Inode allocation.
  - Directory entry insertion.
  - Optional parent pointer space.
- Computes link space reservation:
  - Directory entry insertion.
  - Optional parent pointer space.
- Computes symlink space reservation:
  - Inode allocation.
  - Directory entry insertion.
  - Remote symlink blocks.
  - Optional parent pointer space.
- Computes remove space reservation:
  - Directory removal.
  - Optional parent pointer removal space.
- Computes rename space reservation:
  - Source removal.
  - Target insertion.
  - Parent pointer replacement/removal/addition cases.
  - Whiteout handling.
  - Existing target handling.

## Key Interfaces and Invariants

- Parent pointers are assumed to be first attrs in an attr tree and no larger than one block.
- Parent pointer support increases namespace block reservations.
- Rename reserves for both removal and insertion paths, then layers parent pointer cases depending on whiteout and target existence.
- `xfs_rename_space_res` always adds existing-target parent pointer space, even outside the parent-feature conditional in the current code.

## Dependencies

Depends on transaction space macros, directory/attribute geometry, bmap btree sizing, and parent pointer feature predicates.
