# File Research: sources/os/linux/linux-stable/fs/hfs/super.c

## Scope

Registers the classic HFS filesystem and implements fs-context option parsing, mount, remount, statfs, sync, delayed MDB flushing, superblock teardown, and inode-cache lifecycle.

## APIs And Behavior

- `hfs_sync_fs()` validates counters and commits the MDB.
- `hfs_put_super()` cancels delayed MDB work, marks the MDB clean, and releases MDB resources.
- `hfs_mark_mdb_dirty()` queues delayed MDB writeback on `system_long_wq` unless read-only.
- `hfs_statfs()` reports allocation-block based capacity/free counts and maximum name length.
- `hfs_reconfigure()` handles read-only/read-write transitions while refusing write access to unclean or locked volumes.
- `hfs_show_options()` emits non-default mount options.
- `hfs_parse_param()` parses uid/gid, umasks, partition/session selection, file type/creator, quiet mode, codepage, and iocharset.
- `hfs_fill_super()` initializes `hfs_sb_info`, reads the MDB, finds the root catalog record by `HFS_ROOT_CNID`, loads the root inode, and installs dentry operations.
- Module init/exit creates/destroys the inode slab and registers/unregisters `hfs`.

## State And Dependencies

The file owns `hfs_inode_cachep` and the `file_system_type`. It depends on `hfs_mdb_get/put/commit`, catalog lookup, root inode loading, xattr handlers, NLS option loading, and block-device mount helpers.

## Risks And Invariants

Remount ignores fs-specific option changes and only handles read-only state. Error cleanup after failed `hfs_mdb_get()` calls `hfs_mdb_put()`, so MDB teardown must tolerate partially initialized superblock state. Dirty MDB writeback is delayed and separately flushed by fsync.
