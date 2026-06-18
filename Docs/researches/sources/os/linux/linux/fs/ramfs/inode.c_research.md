# File Research: sources/os/linux/linux/fs/ramfs/inode.c

Common ramfs inode, directory, mount, and filesystem registration code.

Key responsibilities:
- Defines ramfs mount-private state:
  - `struct ramfs_mount_opts`
  - `struct ramfs_fs_info`
- `ramfs_get_inode()` allocates and initializes inodes:
  - sets `ram_aops`,
  - sets high-user GFP mask,
  - marks mapping unevictable,
  - installs file, directory, symlink, or special inode operations.
- Creates filesystem objects:
  - `ramfs_mknod()`
  - `ramfs_mkdir()`
  - `ramfs_create()`
  - `ramfs_symlink()`
  - `ramfs_tmpfile()`
- Defines directory inode operations using simple VFS helpers.
- Shows mount options via `ramfs_show_options()`.
- Defines superblock operations:
  - `simple_statfs`,
  - `inode_just_drop`,
  - `show_options`.
- Parses mount options through fs_context:
  - supports octal `mode=`,
  - accepts source-like parameters,
  - ignores unknown options for historical compatibility.
- `ramfs_fill_super()` initializes superblock fields and creates the root inode/dentry.
- Provides fs_context operations and lifecycle:
  - `ramfs_init_fs_context()`,
  - `ramfs_get_tree()`,
  - `ramfs_free_fc()`,
  - `ramfs_kill_sb()`.
- Registers `ramfs` at `fs_initcall`.

Important behavior:
- `sb->s_d_flags = DCACHE_DONTCACHE`, matching ramfs’s simple/persistent dentry model.
- `FS_USERNS_MOUNT` allows user-namespace mounts.
- Default root mode is `0755`.
- File data lives in page cache; ramfs has no backing store and no reclaimable persistent storage.

Research notes:
- File operation details are supplied by either `file-mmu.c` or `file-nommu.c`.
