# File Research: sources/os/bsd/dragonflybsd/sys/sys/mqueue.h

POSIX message queue public and kernel-internal definitions.

Key responsibilities:
- Defines `MQ_OPEN_MAX`, `MQ_PRIO_MAX`, `mqd_t`, and public `struct mq_attr`.
- Defines kernel-only internal queue flags, name length, default message size, priority queue sizing, and reserved queue index.
- Defines `struct mqueue` with name, lock, sleep channels, attributes, kqueue notification state, signal notification, permissions, refcount, priority queue heads, bitmap, global list entry, and timestamps.
- Defines variable-length `struct mq_msg`.
- Declares kernel initialization and send/receive helper APIs.

Important behavior:
- Internal flags use high bits in `mq_flags`, which the comment notes is POSIX-appropriate.
- Queues use 32 fixed priority queues plus a reserved linear-insertion queue if the priority maximum is expanded.
- Kqueue and signal notification state is embedded directly in each queue.

Dependencies:
- Kernel structures depend on `types.h`, `lock.h`, `queue.h`, `event.h`, and `signal.h`.
- Kernel APIs use `struct lwp`, `mqd_t`, `timespec`, and message buffers.

Notable risks:
- `mq_msg` uses a one-byte flexible tail idiom, so allocation sizing must include payload length.
- Priority bitmap and queue indexing must stay in sync with `MQ_PQSIZE` and `MQ_PRIO_MAX`.
