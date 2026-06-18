# File Research: sources/virtualization/spdk/module/sock/uring/uring.c

Implements SPDK’s Linux io_uring socket backend. It registers a `uring` `spdk_net_impl` only if a probe group can be created successfully.

Key responsibilities:
- Socket lifecycle: listen, connect, dummy async connect, accept, close.
- Socket operations: `recv`, `readv`, `writev`, async write queueing, flush, recv-next, low-water/buffer setters, IPv4/IPv6 checks, connectivity checks.
- io_uring group processing: queue initialization, SQE submission, CQE reaping, read/write/ERRQUEUE/cancel task handling.
- Provided-buffer receive path: io_uring buffer ring registration, tracker management, user buffer acquisition/return through `spdk_sock_group_get_buf()` and `spdk_sock_group_provide_buf()`.
- Optional receive-pipe path mirroring the POSIX implementation.
- Optional zerocopy send handling using ERRQUEUE completions.
- Placement ID lookup and socket-group mapping with `spdk_sock_map`.

Important structures:
- `struct spdk_uring_sock`: wraps `spdk_sock`, fd, per-socket tasks (`write_task`, `read_task`, `errqueue_task`, `cancel_task`), recv stream, recv pipe, zerocopy state, connection status, placement id, and callback data.
- `struct spdk_uring_task`: represents one io_uring operation and stores task type, status, msghdr/iovs, final request pointer, and zerocopy flag.
- `struct spdk_uring_sock_group_impl`: wraps `spdk_sock_group_impl`, owns the `io_uring`, inflight/queued/available counters, pending receive list, buffer ring, tracker array, and free tracker list.
- `struct spdk_uring_buf_tracker`: tracks a user-provided buffer posted to the io_uring buffer ring.

Control flow:
- `uring_sock_create()` handles both listen and connect paths using shared POSIX fd helper routines, then allocates an io_uring socket.
- `uring_sock_connect_async()` is intentionally a dummy async wrapper around synchronous connect; it stores the callback and invokes it during flush/poll, avoiding immediate callback-before-return behavior.
- `uring_sock_group_impl_create()` creates a queue with depth `4096`, registers a provided-buffer ring, and inserts CPU placement mapping if configured.
- `uring_sock_group_impl_add_sock()` initializes per-socket tasks, starts a receive SQE immediately, and starts an ERRQUEUE receive SQE for zerocopy sockets.
- `uring_sock_group_impl_poll()` flushes socket writes, repopulates the buffer ring, submits queued SQEs, reaps completions, and returns sockets with pending receive events.
- `sock_uring_group_reap()` is the central CQE dispatcher for read, write, ERRQUEUE, and cancel completions.
- `uring_sock_group_impl_remove_sock()` synchronously cancels active write/read/errqueue tasks, drains cancel completions through polling, removes pending receive state, releases placement mapping, and detaches the socket from the group.

Dependencies and integration points:
- Requires Linux io_uring via `<liburing.h>`.
- Reuses SPDK POSIX socket fd helpers for address resolution, fd creation, and connect setup.
- Uses SPDK socket request helpers for async write queue handling.
- Uses SPDK socket group buffer APIs for provided-buffer receive mode.
- Constructor `net_impl_register_uring()` creates and closes a probe group before registering `g_uring_net_impl`.

Notes:
- Interrupt mode is explicitly unsupported by `uring_net_impl_init()`.
- TLS fields exist in copied implementation options but this backend does not implement SSL.
- The receive path differs significantly depending on whether `enable_recv_pipe` is set: with pipes, reads can use direct `recvmsg`; without pipes and in a group, io_uring buffer-ring completions populate `recv_stream`.
