# File Research: sources/os/linux/linux/fs/orangefs/orangefs-mod.c

Implements OrangeFS module initialization, teardown, globals, and in-progress operation purge.

Key behavior:
- Defines global stats, hash table size, debug mask, timeout tunables, request mutex, in-progress hash table, request list, locks, and waitqueue.
- Registers filesystem type `pvfs2` with `orangefs_init_fs_context()` and `orangefs_kill_sb()`.
- Module init clamps negative timeouts, initializes operation and inode caches, allocates in-progress hash buckets, initializes fsid key table, prepares debugfs help, initializes debugfs/sysfs/device subsystem, and registers the filesystem.
- Cleanup unregisters filesystem, removes debugfs/sysfs, finalizes fsid/device/caches, asserts request/in-progress lists are empty, and frees hash table.
- `purge_inprogress_ops()` walks all hash buckets and marks each in-progress op purged, completing waiters.

Important dependencies:
- Init order matters because sysfs/debugfs/device and VFS operations rely on operation caches and global queues.
