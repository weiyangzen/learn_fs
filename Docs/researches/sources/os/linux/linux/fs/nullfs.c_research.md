# File Research: sources/os/linux/linux/fs/nullfs.c

## Role

Defines a minimal internal Linux filesystem named `nullfs`. It creates a single global, non-user-mountable, permanently empty, immutable directory superblock.

## Major Contents

- `nullfs_super_operations`:
  - Only provides `.statfs = simple_statfs`.
- `nullfs_fs_fill_super()`:
  - Initializes superblock limits, block size, magic, operations, time granularity, and flags.
  - Allocates one inode, converts it to an empty directory, initializes timestamps, assigns inode number 1, marks it immutable, and installs it as root.
- `nullfs_fs_get_tree()`:
  - Uses `get_tree_single()` to enforce a single global instance.
- `nullfs_init_fs_context()`:
  - Sets fs context operations.
  - Marks the context global.
  - Sets `SB_NOUSER`.
  - Sets internal flags `SB_I_NOEXEC | SB_I_NODEV`.
- `nullfs_fs_type`:
  - Registers name `nullfs`, init context, and `kill_anon_super`.

## Important Invariants

- The filesystem is intentionally empty and immutable.
- It is not mountable by userspace due `SB_NOUSER`.
- It is currently single-instance/global.
- Root inode allocation failure returns `-ENOMEM`.

## Dependencies

- Linux superblock/fs_context APIs.
- `NULL_FS_MAGIC`.
- Simple directory/statfs helpers.

## Notes For Future Work

- Comments note it could become userspace-mountable and multi-instance later.
- In `nullfs_fs_fill_super()`, if `d_make_root()` fails it returns `-ENOMEM`; `d_make_root()` consumes the inode on failure, so the usual ownership pattern is preserved.
