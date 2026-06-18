# sources/test-tools/strace/bundled/linux/include/uapi/linux/mqueue.h

Purpose: defines POSIX message queue ABI constants, queue attribute layout, and special netlink-cookie behavior for user-space `SIGEV_THREAD` notification emulation.

Important APIs/types/functions: exports `MQ_PRIO_MAX`, `MQ_BYTES_MAX`, `struct mq_attr`, notification codes `NOTIFY_NONE`, `NOTIFY_WOKENUP`, `NOTIFY_REMOVED`, and `NOTIFY_COOKIE_LEN`.

Control flow: `mq_open`, `mq_getsetattr`, send/receive, and notify syscalls use `mq_attr` for flags, queue depth, message size, and current message count. For `SIGEV_THREAD`, libc uses an AF_NETLINK socket and a fixed-size cookie to receive notification completion/removal messages.

State/persistence behavior: message queues persist as kernel IPC objects until unlinked/closed per POSIX rules. `mq_attr` changes can affect nonblocking behavior; notification registration is one-shot mutable queue state.

Dependencies/integration: depends on Linux integer types and integrates with POSIX mqueue syscalls, libc notification helpers, netlink sockets, and per-UID resource limits.

Risks and test signals: long-size fields vary by ABI and notification cookie semantics are unusual. Tests should decode `mq_attr` in syscalls, queue limits, and `mq_notify` `SIGEV_THREAD` netlink-cookie paths.
