# File Research: sources/os/linux/linux/fs/file_table.c

Read status: complete, 667 lines.

Purpose: allocates, initializes, accounts, and releases global `struct file` objects.

Key flow:
- Maintains `/proc/sys/fs/file-nr`, `file-max`, and `nr_open` sysctls with a percpu `nr_files` counter.
- `init_file()` initializes credentials, security state, locks, fsnotify mode, f_mode/f_flags, error samples, and `f_ref`.
- `alloc_empty_file()`, `alloc_empty_file_noaccount()`, and `alloc_empty_backing_file()` allocate regular, unaccounted, or backing-file wrappers.
- `file_init_path()`, `alloc_file_pseudo()`, `alloc_file_pseudo_noaccount()`, and `alloc_file_clone()` bind files to paths/inodes/file-ops.
- `__fput()` performs final close teardown: fsnotify close, epoll release, locks, LSM release, fasync, file op release, cdev put, fops put, owner/access/path/mount cleanup, and file cache free.
- `fput()` defers final teardown through task work when possible, with delayed work fallback for interrupts/kernel threads; sync variants run immediate final put.

Important dependencies: LSM, fsnotify, epoll, file locks, cdevs, mount lifetime, percpu counters, SLAB_TYPESAFE_BY_RCU caches.

Risk/concurrency notes:
- `struct file` cache is `SLAB_TYPESAFE_BY_RCU`; initialization places `f_ref` last so RCU lookup users never see partially reinitialized state as valid.
- Deferred fput paths must avoid deadlocks around umount and kernel thread contexts.
