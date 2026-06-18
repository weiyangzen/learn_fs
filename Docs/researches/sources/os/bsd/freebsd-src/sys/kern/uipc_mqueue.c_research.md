# File Research: sources/os/bsd/freebsd-src/sys/kern/uipc_mqueue.c

## Purpose
Implements FreeBSD POSIX message queues and the synthetic `mqueuefs` filesystem view. Queues can be accessed through `kmq_*` syscalls without mounting the filesystem, while mounted `mqueuefs` exposes queue names as regular-looking vnode entries whose reads report queue statistics.

## Main Elements
- `mqfs_node`, `mqfs_info`, and `mqfs_vdata`: in-kernel namespace tree, vnode attachments, reference counts, file numbers, ownership/mode metadata, timestamps, and jail-root visibility tags.
- `struct mqueue`: queue state including limits, current messages, total queued bytes, priority-ordered message list, sender/receiver wait counters, select/kqueue state, and optional `mq_notify()` registration.
- `mqfs_init()` / `mqfs_uninit()`: create UMA zones, initialize the single global namespace root, add `.` and `..`, register process-exit cleanup, publish POSIX feature config, and register jail OSD cleanup.
- VFS/vnode operations: mount/unmount/root/statfs, vnode allocation/recycling, lookup/create/remove, inactive/reclaim, access/getattr/setattr, read, and readdir.
- Queue operations: `mqueue_alloc()`, `mqueue_free()`, `mqueue_send()`, `_mqueue_send()`, `mqueue_receive()`, `_mqueue_recv()`, and message copyin/copyout helpers.
- Syscall entry points: `kern_kmq_open()`, `sys_kmq_open()`, `sys_kmq_unlink()`, `kern_kmq_setattr()`, send/receive timed wrappers, and notify wrappers.
- Descriptor operations: `mqueueops` supports poll, kqueue, stat, close/fdclose, chmod/chown, `kinfo_file`, and descriptor passing.
- Notification support: per-process `mqueue_notifier` list, `mq_proc_exit()` cleanup, `SIGEV_SIGNAL`/`SIGEV_THREAD_ID`/`SIGEV_NONE` validation, and one-shot notification delivery.
- `COMPAT_FREEBSD32` wrappers translate `mq_attr`, `timespec`, and `sigevent` layouts and register 32-bit syscall helpers.

## Dependencies And Integration
Integrates VFS, vnode cache, file descriptors, Capsicum rights (`cap_read_rights`, `cap_write_rights`, `cap_event_rights`), audit, jails, process exit eventhandlers, POSIX.1b feature reporting, UMA, taskqueue vnode recycle, select, kqueue, signals, and syscall helper registration. The namespace is global but filters lookup/readdir by jail root.

## Risk Notes
Correctness depends on lock partitioning between the global `mqfs_data.mi_lock` namespace lock and per-queue `mq_mutex`. Queue deletion unlinks names but open descriptors keep node/queue references alive. `mq_notify()` races are handled by rechecking the fd under `FILEDESC_SLOCK` and using per-process notifier cleanup, but signal queue ownership and descriptor reuse remain subtle. Timeout logic uses absolute timespecs and converts to ticks in retry loops; invalid nanoseconds are rejected after an initial nonblocking attempt, matching the file's current behavior.
