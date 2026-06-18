# File Research: sources/os/linux/linux-stable/fs/orangefs/devorangefs-req.c

## Scope

This file implements the `/dev/pvfs2-req` character device that connects kernel VFS operations to the OrangeFS userspace client daemon.

## APIs Covered

- Device file operations: `orangefs_devreq_open()`, `orangefs_devreq_read()`, `orangefs_devreq_write_iter()`, `orangefs_devreq_release()`, ioctl, compat ioctl, and poll.
- Operation tracking: in-progress hash add/remove by operation tag.
- Daemon state: `is_daemon_in_service()`, `__is_daemon_in_service()`, single-open enforcement, userspace protocol version tracking.
- Ioctls: magic/size queries, shared buffer map installation, remount-all, upstream-kmod marker, and debugfs client/kernel mask updates.
- Device lifecycle: `orangefs_dev_init()` and `orangefs_dev_cleanup()`.

## Control Flow And Behavior

- The device can be opened only once, only from `init_user_ns`, and only with `O_NONBLOCK`.
- Reads copy protocol version, magic, tag, and upcall to userspace, then mark the op in progress and insert it into the in-progress hash.
- Reads skip operations for filesystems pending remount or unknown filesystems except mount/getattr/unmount cases.
- Writes parse header and downcall, validate protocol version and magic, remove the matching op by tag, optionally copy a READDIR trailer, and complete the waiting operation.
- Device release finalizes bufmap state, marks mounted filesystems pending remount, purges waiting and in-progress ops, runs down shared-memory slots, and clears daemon version state.
- `ORANGEFS_DEV_REMOUNT_ALL` serializes with `orangefs_request_mutex` and remounts tracked superblocks while carefully dropping the superblock spinlock around blocking work.

## State, Dependencies, And Invariants

- Uses global request list, in-progress hash table, wait queue, and per-op spinlocks.
- Shared-memory buffer map setup is delegated to `orangefs_bufmap_initialize()`.
- READDIR is the only operation allowed to carry a downcall trailer.
- Cancel and given-up operations require special completion/release handling.
- Protocol header sizes and magic must match userspace client expectations.
