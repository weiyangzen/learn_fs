# File Research: sources/os/bsd/openbsd-src/sys/kern/sysv_msg.c

Implements System V message queues.

Global state:
- `msg_queues`: global TAILQ of active queues.
- `sysvmsgpl`: pool for `struct msg`.
- `msginfo`: tunables/limits such as max message size, queue count, queue bytes, and total messages.
- `num_ques`, `num_msgs`, `sequence`, `maxmsgs`: queue/message accounting and sequence generation.

Syscall behavior:
- `msginit()` initializes tunables, the message pool, and global queue state.
- `sys_msgget()` looks up or creates a queue by key, enforces `IPC_CREAT`/`IPC_EXCL`, permission checks, and max queue count.
- `sys_msgsnd()` checks queue existence, message size limits, write permission, queue byte space, and total message limit; it sleeps unless `IPC_NOWAIT`, copies message data from userland into mbufs, enqueues, and wakes readers.
- `sys_msgrcv()` checks read permission, finds a matching message by type rule, sleeps unless `IPC_NOWAIT`, copies out without losing the message on copyout error, dequeues on success, wakes writers, and returns copied size.
- `sys_msgctl()` implements `IPC_RMID`, `IPC_SET`, and `IPC_STAT`.

Queue and message lifecycle:
- Queue ids combine a queue index with an IPC sequence value.
- `que_create()` keeps queues ordered by index and handles key races caused by sleeping allocation.
- `QREF`/`QRELE` reference management is used while removing queues so waiters and active callers see `MSGQ_DYING` and unwind cleanly.
- `msg_create()` uses the pool and detects queues removed during allocation.
- `msg_free()` frees mbuf chains and decrements global message count.

Message storage:
- The user buffer layout is a leading `long` message type followed by opaque bytes.
- Message payloads are stored in mbuf chains, using clusters for larger messages.
- `msg_lookup()` implements System V type matching: exact positive type, any type for zero, and bounded match for negative types.

Sysctl export:
- `sysctl_sysvmsg()` exports `msginfo` and an array of `msqid_ds` entries for compatibility with `ipcs(1)`, preserving old array-index behavior.

Filesystem/storage relevance:
- Not filesystem code. Relevant as kernel object lifetime, permission, wait/wakeup, and copyin/copyout infrastructure that parallels many VFS object-management patterns.
