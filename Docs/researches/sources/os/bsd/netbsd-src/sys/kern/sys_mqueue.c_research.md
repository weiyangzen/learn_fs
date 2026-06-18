# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_mqueue.c

## Purpose
Implements POSIX message queues as named, descriptor-backed kernel objects with send/receive, timed waits, notification, attributes, unlink, poll, stat, sysctl, and module registration.

## Main Interfaces
- Module/syscall setup: `mqueue_sysinit`, `mqueue_sysfini`, `mqueue_modcmd`, `mqueue_syscalls`.
- Open/lookup: `mq_handle_open`, `mqueue_create`, `mqueue_lookup`, `mqueue_get`.
- I/O: `mq_send1`, `sys_mq_send`, `sys___mq_timedsend50`, `mq_recv1`, `sys_mq_receive`, `sys___mq_timedreceive50`.
- Control: `sys_mq_notify`, `sys_mq_getattr`, `sys_mq_setattr`, `sys_mq_unlink`, `sys_mq_close`.
- Fileops: `mq_poll_fop`, `mq_stat_fop`, `mq_close_fop`.

## State And Control Flow
A global `mqueue_head` name list is protected by `mqlist_lock`; each queue has `mq_mtx`, condition variables, select info, reference count, attributes, owner/mode, message priority queues, and optional notification target. Send allocates/copies a message, blocks while full unless nonblocking/timed out, inserts by priority, optionally sends SIGEV_SIGNAL notification, then wakes receivers. Receive blocks while empty, removes the highest-priority message, wakes senders, and copies message/prio to userland after releasing the queue lock.

## Dependencies And Integration
Uses descriptor `fileops`, per-process mqueue count accounting, `genfs_can_access` for mode checks, kauth for unlink permissions, pool cache for default-sized messages, condition variables, poll/select, signals, sysctl tunables, and module syscall establishment.

## Risks And Edge Cases
- POSIX says a receive should not remove a message if copyout fails; the code comments acknowledge this can be violated.
- `mq_setattr` applies `O_NONBLOCK` before optional old-attribute copyout, also noted as POSIX-sensitive on copyout failure.
- `mq_prio_max` sysctl growth can force high-priority messages into a reserved sorted queue.
- Unlink removes the name, marks live queues `MQ_UNLINKED`, wakes blocked send/receive waiters, and defers destruction until last close.

## Filesystem Relevance
Moderate. POSIX mqueues are named descriptor objects with permission/mode/stat behavior resembling filesystem nodes, but they live in kernel lists rather than VFS directories.
