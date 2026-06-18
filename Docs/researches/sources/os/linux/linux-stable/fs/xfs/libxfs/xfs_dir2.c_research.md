# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_dir2.c

## Role
`xfs_dir2.c` is the generic XFS directory operation layer. It dispatches directory create, lookup, remove, replace, grow, shrink, and higher-level child update operations to the correct shortform/block/leaf/node implementation.

## Main Responsibilities
- Define canonical `.` and `..` names and convert inode modes to directory file types.
- Provide ASCII case-insensitive hashing and comparison for filesystems with the legacy ascii-ci feature.
- Allocate and initialize directory and attribute DA geometry at mount time.
- Determine a directory's current format from inode fork format and mapped EOF.
- Build `xfs_da_args` and dispatch createname, lookup, removename, and replace operations to format-specific helpers.
- Grow and shrink directory data/free blocks.
- Validate directory entry names and inode numbers.
- Coordinate higher-level link, unlink, rename, exchange, whiteout, parent-pointer, and live-hook behavior.

## Important Functions
- `xfs_da_mount` initializes `m_dir_geo` and `m_attr_geo`, computing block sizes, header sizes, leaf/free/node capacities, logical segment starts, max extents, and magic free-space thresholds.
- `xfs_dir2_format` returns shortform, block, leaf, node, or error based on local fork status and last mapped offset.
- `xfs_dir_createname`, `xfs_dir_lookup`, `xfs_dir_removename`, and `xfs_dir_replace` allocate and populate `xfs_da_args`, including hash, fork, transaction, owner, and operation flags.
- `xfs_dir2_grow_inode` allocates directory data/free-space blocks and grows `i_disk_size` for data-space additions.
- `xfs_dir2_shrink_inode` unmaps directory data/free blocks, invalidates buffers, and trims `i_disk_size` when removing trailing data blocks.
- `xfs_dir_create_child`, `xfs_dir_add_child`, and `xfs_dir_remove_child` implement VFS-level child link/unlink semantics, link count updates, parent pointer updates, and directory update hooks.
- `xfs_dir_exchange_children` swaps two existing directory entries and adjusts `..` entries and link counts for directory moves across parents.
- `xfs_dir_rename_children` implements rename with replacement and optional whiteout handling, including target setup, source cleanup, parent pointer updates, and hook notifications.

## Invariants
- Directory operations assert directory inode mode and required inode locks for high-level child updates.
- Inode numbers are validated through `xfs_dir_ino_validate` before insertion or replacement.
- Shortform empty-directory checks assume only `.` and `..` are present when the shortform count is zero.
- The format detector treats local fork data as shortform, one data block as block format, data plus one leaf block as leaf format, and larger layouts as node format.
- Rename and exchange model hook notifications as removals before additions so clients can process changes consistently while locks are held.

## Error Handling
- Corrupt format state marks directory data sick and returns `-EFSCORRUPTED`.
- Expected semantic failures such as non-empty directory removal use `-ENOTEMPTY` or `-EEXIST`.
- No-space checks are supported through `xfs_dir_canenter` and `XFS_DA_OP_JUSTCHECK`.
- `xfs_dir2_shrink_inode` deliberately leaves a block mapped if unmapping returns an error such as no reservation for a bmap split.

## Dependencies
This file bridges VFS-facing directory behavior with format-specific files such as shortform, block, leaf, node, data, and parent-pointer code. It also touches bmap, transaction, inode link count, AG unlink-list, live hooks, and health subsystems.

## Research Notes
The central pattern is format dispatch through `xfs_dir2_format` plus shared `xfs_da_args`. Higher-level directory mutation code is careful to stage link counts, `..` entries, parent pointers, and hook notifications in transaction-safe order.
