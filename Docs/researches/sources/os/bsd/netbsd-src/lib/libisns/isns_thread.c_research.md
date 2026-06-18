# File Research: sources/os/bsd/netbsd-src/lib/libisns/isns_thread.c

Implements the libisns control thread and kqueue event handlers. The control loop drains queued tasks when no current task is active, then waits for pipe/socket/timer events via `kevent()`.

Key behavior:
- `isns_get_next_task()` requeues non-init tasks and creates a reconnect task when the socket is disconnected.
- `isns_kevent_pipe()` consumes command bytes for processing the task queue, aborting a transaction, or stopping the thread.
- `isns_kevent_socket()` incrementally reads PDU headers and payloads into buffer chains, validates protocol version, converts header fields to host order, and completes matching transactions once all response PDUs arrive.
- Reconnect and refresh timer handlers recreate sockets or send periodic `DevAttrQry` refresh transactions.

Notable risks:
- Header reads have an explicit TODO for short header reads; current code subtracts a full header size after one `readv()`.
- Static `read_buf` assumes serialized access.
- Some response validation is narrow: unsolicited or duplicate PDUs are freed rather than surfaced.
