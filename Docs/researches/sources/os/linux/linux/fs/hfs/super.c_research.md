# File Research: sources/os/linux/linux/fs/hfs/super.c

Purpose: Implements classic HFS filesystem registration, mount context parsing, superblock operations, delayed MDB flushing, root inode setup, and inode cache management.

Key functions:
- `hfs_sync_fs()` validates counters and commits MDB state.
- `hfs_put_super()` cancels delayed work, closes MDB, and releases resources.
- `flush_mdb()` is the delayed work handler for MDB commits.
- `hfs_mark_mdb_dirty()` schedules delayed MDB writeback.
- `hfs_statfs()` reports block/free counts based on allocation blocks.
- `hfs_reconfigure()` handles remount and refuses unsafe read-write transitions.
- `hfs_show_options()` prints non-default mount options.
- `hfs_parse_param()` handles uid/gid/umask/type/creator/partition/session/NLS/quiet options.
- `hfs_fill_super()` initializes HFS state, reads MDB, opens catalog, finds root, sets dentry operations, and creates root dentry.
- Module init/exit create/destroy the HFS inode slab and register/unregister the filesystem.

Dependencies and integration:
- Uses FS context API, `hfs_mdb_get()`, catalog lookup, inode creation, and xattr handlers.
- Sets `SB_NODIRATIME` and `FS_REQUIRES_DEV`.

Risk notes:
- Remount read-write is blocked for unclean or locked volumes.
- Mount option parsing rejects repeated NLS changes and non-4-byte type/creator strings.
