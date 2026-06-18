# File Research: sources/os/linux/linux-stable/fs/nullfs.c

Purpose: Defines a minimal internal `nullfs` filesystem that provides one permanently empty, immutable root directory.

Key responsibilities:
- Supplies `nullfs_super_operations` with `simple_statfs`.
- Fills a single anonymous superblock in `nullfs_fs_fill_super()`, setting maxbytes, block size, magic, super operations, time granularity, and no xattrs/export operations.
- Allocates root inode, initializes it as an empty directory, sets inode number 1, timestamps, and `S_IMMUTABLE`.
- Uses `get_tree_single()` to provide one global instance.
- Initializes fs_context with `fc->global = true`, `SB_NOUSER`, and internal noexec/nodev flags.
- Exposes `struct file_system_type nullfs_fs_type`.

Important invariants:
- The filesystem is not user-mountable (`SB_NOUSER`) and is intended as a single global internal instance.
- Root is empty and immutable by construction.
- `kill_anon_super` tears down the anonymous superblock.

Dependencies:
- Uses simple VFS helpers: `new_inode()`, `make_empty_dir_inode()`, `simple_inode_init_ts()`, `d_make_root()`, `get_tree_single()`, and `kill_anon_super()`.

Risk notes:
- If `d_make_root()` fails, the function returns `-ENOMEM`; `d_make_root()` consumes the inode, so this path relies on VFS ownership semantics.
