# File Research: sources/os/linux/linux-stable/fs/orangefs/orangefs-mod.c

## Scope

This file implements OrangeFS module lifecycle, module parameters, global request queues, filesystem registration, and in-progress operation purge.

## APIs Covered

- Module init/exit: `orangefs_init()`, `orangefs_exit()`.
- Global operation state: request mutex, in-progress hash table, request list, request-list lock, and request-list wait queue.
- `purge_inprogress_ops()`.

## Control Flow And Behavior

- Init normalizes negative timeouts, creates operation and inode caches, allocates in-progress hash buckets, initializes fsid key table, prepares debugfs help, initializes debugfs/sysfs/device layers, and registers filesystem type `pvfs2`.
- Error paths unwind in reverse order.
- Exit unregisters filesystem, removes debugfs/sysfs, finalizes fsid/device/cache state, asserts request and in-progress lists are empty, and frees hash storage.
- `purge_inprogress_ops()` walks all hash buckets and marks each operation purged so waiters can retry or fail after daemon shutdown.

## State And Dependencies

- Module parameters include hash table size, debug mask, operation timeout, and slot timeout.
- Global cache and dcache/getattr timeout defaults are exported for sysfs.
- Filesystem type uses `orangefs_init_fs_context()`, `orangefs_fs_param_spec`, and `orangefs_kill_sb()` from superblock code.

## Risks And Invariants

- Request structures must be empty on unload.
- Hash table size controls tag lookup distribution for downcalls.
- Device initialization must occur before normal mounted operation can be serviced.
