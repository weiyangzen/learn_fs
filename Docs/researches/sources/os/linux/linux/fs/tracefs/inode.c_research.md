# File Research: sources/os/linux/linux/fs/tracefs/inode.c

Purpose: General tracefs filesystem implementation: inode cache, mount options, filesystem registration, file/dir creation helpers, recursive removal, and interaction with eventfs.

Key APIs:
- `tracefs_get_inode()`
- `tracefs_start_creating`, `tracefs_failed_creating`, `tracefs_end_creating`
- `tracefs_create_file()` exported GPL
- `tracefs_create_dir()`
- `tracefs_create_instance_dir()`
- `tracefs_remove()`
- `tracefs_initialized()`

Implementation notes:
- Maintains a custom `tracefs_inode` slab cache and a global RCU list of tracefs inodes for remount ownership propagation.
- Mount options: `uid`, `gid`, `mode`; default mode is `0700`.
- `tracefs_apply_options()` updates root inode mode/ownership and, on remount, clears per-inode saved UID/GID flags and calls `eventfs_remount` for eventfs inodes.
- Instance directory supports userspace mkdir/rmdir callbacks and temporarily drops inode locks while invoking tracing callbacks.
- Creation helpers pin the tracefs mount with `simple_pin_fs`, create persistent dentries, initialize ownership from parent, and emit fsnotify events.
- Lockdown check `LOCKDOWN_TRACEFS` suppresses tracefs/eventfs file creation.

Concurrency and correctness:
- `tracefs_inode_lock` protects global inode list updates.
- Dentry ops use `d_fsdata` to distinguish eventfs dentries, route release to eventfs, and invalidate freed eventfs nodes.
- `tracefs_drop_inode()` clears eventfs flag before inode teardown to avoid remount updates racing stale eventfs state.
