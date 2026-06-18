# File Research: sources/os/linux/linux/fs/kernfs/file.c

Purpose: Implements kernfs regular file behavior: open/release, seq-file reads, binary reads/writes, mmap wrapping, poll/notify, draining open files during node teardown, and internal file-node creation.

Key structures and state:
- `struct kernfs_open_node` tracks all open instances for a kernfs node, poll waitqueue, event counter, mmap count, and pending release count.
- `struct kernfs_open_file` instances are linked into the open node and serialize per-open operations through `of->mutex`.
- `kn->attr.open` is RCU-published and updated under the per-node hashed mutex from `kernfs_node_lock_ptr()`.

Main control flow:
- `kernfs_fop_open()` validates permissions, allocates and initializes `kernfs_open_file`, creates a seq_file wrapper, links into `kernfs_open_node`, and invokes optional `ops->open`.
- Read dispatch chooses `seq_read_iter()` when `KERNFS_HAS_SEQ_SHOW` is set, otherwise uses a page-sized/preallocated buffer and calls `ops->read`.
- Write copies user data into a NUL-terminated buffer, honors `atomic_write_len`, and calls `ops->write`.
- `kernfs_fop_mmap()` invokes `ops->mmap`, wraps VMA ops with `kernfs_vm_ops`, and rejects incompatible remaps or VM close callbacks.
- `kernfs_notify()` immediately updates poll state, then schedules work to emit fsnotify events across all mounted kernfs superblocks.
- `kernfs_drain_open_files()` unmaps active mappings and forces release callbacks before node removal completes.

Dependencies and integration:
- Exports `kernfs_notify()` and `kernfs_file_fops`.
- Depends on `kernfs_get_active()`/`kernfs_put_active()` from directory/core kernfs code, inode lookup for fsnotify, and `kernfs_root()->supers` for multi-superblock notification.
- Uses VFS seq_file, poll, mmap, splice, fsnotify, RCU, wait queues, and hashed kernfs node locks.

Concurrency and risk notes:
- Active references protect `kn->attr.ops`; open-file mutex serializes callbacks for one open file.
- The `ERR_PTR(-ENODEV)` seq iteration convention is delicate because custom seq ops may return the same sentinel.
- Release and drain paths intentionally avoid `of->mutex` to prevent lock dependency cycles.
- Notification list uses a self-pointer end marker and spinlock; incorrect `notify_next` handling could lose events or leak node refs.
