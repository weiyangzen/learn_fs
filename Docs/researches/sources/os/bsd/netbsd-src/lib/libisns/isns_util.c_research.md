# File Research: sources/os/bsd/netbsd-src/lib/libisns/isns_util.c

Provides libisns command signaling, kqueue event update helpers, config allocation/destruction, control-thread creation/join, and connection-loss retry handling.

Key behavior:
- Commands are written to the control pipe, optionally with payload data via `writev()`.
- `isns_new_config()` initializes file descriptors, socket/PDU/refresh state, task and transaction mutexes, the task queue, and allocates a pthread handle.
- `isns_destroy_config()` closes descriptors, frees refresh transactions, completes pending send tasks, drains the task queue, destroys mutexes, frees copied addrinfo pieces, and frees config storage.
- `isns_process_connection_loss()` retries a send transaction up to three disconnects by freeing partial responses and requeueing the current task.

The thread creation path uses NetBSD `pthread_attr_setname_np()` to name the control thread `isns_control`.
