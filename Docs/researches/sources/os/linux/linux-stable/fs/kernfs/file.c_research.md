# File Research: sources/os/linux/linux-stable/fs/kernfs/file.c

Implements kernfs regular-file behavior: open/release, read/write dispatch, seq_file support, mmap wrapping, poll notifications, open-file draining, and internal file-node creation.

Key structures and state:
- `struct kernfs_open_node` stores per-kernfs-node open-file state: poll event counter, wait queue, open file list, mmap count, and pending release count.
- Each `struct kernfs_open_file` is linked under `kn->attr.open` while open.
- Open-file list updates are protected by a hashed global `kernfs_locks->open_file_mutex[]`.
- Active references via `kernfs_get_active()` protect callback dispatch into `kernfs_ops`.

Major flows:
- `kernfs_fop_open()` validates permissions when `KERNFS_ROOT_EXTRA_OPEN_PERM_CHECK` is set, allocates `kernfs_open_file`, sets up optional preallocation, opens seq_file state, links the open file, and calls `ops->open`.
- Read path uses `seq_read_iter()` when `KERNFS_HAS_SEQ_SHOW` is set; otherwise `kernfs_file_read_iter()` invokes `ops->read` with a PAGE_SIZE-capped buffer.
- Write path copies a single user buffer, NUL-terminates it, honors `atomic_write_len`, and calls `ops->write`.
- mmap path requires cached `KERNFS_HAS_MMAP`, calls `ops->mmap`, rejects close callbacks in supplied VM ops, then wraps fault/open/page_mkwrite/access through `kernfs_vm_ops`.
- Release path calls `ops->release` exactly once when `KERNFS_HAS_RELEASE` is set, unlinks the open file, releases seq state, and frees buffers.
- `kernfs_drain_open_files()` unmaps mmapped files and forces release callbacks during node deactivation.
- `kernfs_notify()` wakes poll waiters immediately, increments event counters, then queues work for fsnotify events across mounted superblocks.
- `__kernfs_create_file()` creates a `KERNFS_FILE` node, stores `kernfs_ops`, size, namespace, private pointer, optional lockdep map, and caches operation-presence flags.

Concurrency and correctness notes:
- `of->mutex` serializes operations for one open file and nests outside active refs.
- The seq_file start/stop path has special handling for `ERR_PTR(-ENODEV)` so active refs are not double-dropped.
- Notification queuing uses `kn->attr.notify_next` as a singly linked membership marker and terminates with `KERNFS_NOTIFY_EOL`.
- Open-node lifetime is RCU-managed with `kfree_rcu`.
