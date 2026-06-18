# File Research: sources/os/bsd/netbsd-src/lib/libisns/isns.c

Public lifecycle and connection setup implementation for `libisns`.

Functions:
- `isns_init` allocates config, creates a control pipe, creates a kqueue, registers pipe events, initializes buffer pools, starts the control thread, and returns an opaque handle.
- `isns_add_servercon` deep-copies an `addrinfo`, creates an init-socket task, queues it, signals processing, and waits for task completion.
- `isns_init_reg_refresh` creates a refresh task for a node and interval.
- `isns_stop` issues stop, destroys the thread/config, and destroys buffer pools.

The implementation is task-queue driven and hides internal config behind `ISNS_HANDLE`.
