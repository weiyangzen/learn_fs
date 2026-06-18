# File Research: sources/local-fs/ocfs2-tools/fswreck/quota.c

This file corrupts OCFS2 global user/group quota files.

Key behavior:
- Requires both user and group quota read-only compatible features.
- Initializes quota info for `USRQUOTA` and `GRPQUOTA`.
- `o2fswreck_read_blk()` and `o2fswreck_write_blk()` read/write quota-file logical blocks through `ocfs2_file_read()` and `ocfs2_file_write()`.
- `o2fswreck_get_data_blk()` recursively walks the quota tree to find a data block and records its block reference in global `g_actref`.
- `QMAGIC_INVALID` flips a user quota header magic after endian swapping.
- `QTREE_BLK_INVALID` corrupts a group quota tree block trailer checksum/ECC.
- `DQBLK_INVALID` corrupts a user quota data entry and leaf header free-list/entry counts.
- `DUP_DQBLK_INVALID` duplicates a group quota ID but gives the duplicate invalid limits and corrupts the leaf header.
- `DUP_DQBLK_VALID` duplicates a group quota ID with copied limit values.

Integration notes:
- Uses quota endian-swap helpers for on-disk structures.
- Allocates `tree_depth + 1` blocks as traversal/read scratch space.
- The global `g_actref` is a traversal side channel for writing the found data block back.
