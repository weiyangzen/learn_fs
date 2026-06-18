# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_dir2.c

## Scope

This file implements the generic XFS directory API above the specific shortform, block, leaf, and node directory formats. It initializes DA geometry, validates inode numbers and names, dispatches create/lookup/remove/replace operations by current directory format, handles ASCII case-insensitive hashing/comparison, grows/shrinks directory data/free spaces, and coordinates child create/link/unlink/rename/exchange operations with link counts, parent pointers, whiteouts, timestamps, and live hooks.

## Main Interfaces

- Constants and helpers: `xfs_name_dot`, `xfs_name_dotdot`, `xfs_mode_to_ftype()`, `xfs_dir2_namecheck()`.
- Case-insensitive support: `xfs_ascii_ci_hashname()`, `xfs_ascii_ci_compname()`, `xfs_dir2_hashname()`, `xfs_dir2_compname()`.
- Mount geometry: `xfs_da_mount()`, `xfs_da_unmount()`.
- Directory format and operations: `xfs_dir2_format()`, `xfs_dir_init()`, `xfs_dir_createname()`, `xfs_dir_lookup()`, `xfs_dir_removename()`, `xfs_dir_replace()`, `xfs_dir_canenter()`.
- Args-level dispatch: `xfs_dir_createname_args()`, `xfs_dir_lookup_args()`, `xfs_dir_removename_args()`, `xfs_dir_replace_args()`.
- Directory block management: `xfs_dir2_grow_inode()`, `xfs_dir2_shrink_inode()`.
- Child update orchestration: `xfs_dir_create_child()`, `xfs_dir_add_child()`, `xfs_dir_remove_child()`, `xfs_dir_exchange_children()`, `xfs_dir_rename_children()`.
- Optional live hooks: `xfs_dir_update_hook()`, hook add/delete/setup/enable/disable functions under `CONFIG_XFS_LIVE_HOOKS`.

## Control Flow And Behavior

`xfs_da_mount()` builds separate directory and attribute geometries from superblock block size, directory block log, CRC feature state, and large extent count support. Directory geometry computes data, leaf, and free space boundaries, node capacity, free index capacity, and first data offset after `.` and `..`.

The generic directory operations allocate and populate `xfs_da_args`, compute the name hash, set owner/fork/transaction fields, and dispatch based on `xfs_dir2_format()`. Shortform, single-block, leaf, and node directories are handled by specialized files. Lookup returns `0` to callers after translating internal `-EEXIST` success, and optional case-insensitive lookup can return the actual matching name.

Directory growth allocates data/free blocks via DA allocation helpers and updates inode size for data-space growth. Shrink unmaps directory data/free blocks, invalidates buffers, and reduces inode size when the removed data block was the last directory data block.

Higher-level child operations maintain VFS-visible metadata. Creating or adding a child inserts the dirent, updates parent timestamps, initializes child directories, bumps link counts, removes tmpfile inodes from the unlinked list when needed, and adds parent pointer attributes when enabled. Removing a child verifies empty directories, adjusts `.` and `..` link counts, rewrites removed directory `..` to root when necessary, removes parent pointer attrs, and emits live hooks.

Rename and exchange handle cross-directory moves, directory `..` replacement, target overwrite link count drops, whiteout insertion, parent pointer replacement/removal/addition, inode ctime updates, and hook notifications modeled as remove events followed by add events.

## State And Data Structures

- Uses `xfs_da_geometry` stored in `m_dir_geo` and `m_attr_geo`.
- Uses `xfs_da_args` as the dispatch object for all format-specific directory operations.
- Uses `xfs_dir_update` to pass directory, child, name, and parent-pointer arguments to child update helpers.
- Optional hook payload is `xfs_dir_update_params`.

## Dependencies

Depends on shortform/block/leaf/node directory implementations, DA Btree allocation, bmap helpers, inode link count helpers, transaction inode logging, parent pointer attribute code, unlinked-list removal, per-AG lookup, live hook infrastructure, and health marking.

## Risks And Invariants

- Format detection assumes data fork locking and validates single-block directories by both EOF and inode disk size.
- Directory inode numbers are validated before insertion and lookup results are checked against filesystem inode constraints.
- Link count and `..` updates must remain transactionally consistent across create, remove, rename, exchange, and whiteout paths.
- Parent pointer updates must match dirent updates exactly or online repair and reverse lookup semantics break.
- Live hook enable/disable uses static branch patching and must not be called while holding reclaim-sensitive locks.
