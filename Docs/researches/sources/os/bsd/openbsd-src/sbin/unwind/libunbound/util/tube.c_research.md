# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/tube.c

Implements Unbound’s “tube” pipe/message service with separate Unix and Winsock implementations.

Unix implementation:
- `tube_create` allocates a tube, creates a `socketpair(AF_UNIX, SOCK_STREAM)` or falls back to `pipe`, stores read/write fds, and sets both nonblocking.
- Messages are framed as a 32-bit length followed by payload bytes.
- `tube_write_msg` can test an initial nonblocking write, then switches the fd to blocking to finish length and payload, restoring nonblocking before return.
- `tube_read_msg` similarly reads the length and payload, rejects messages of at least `65536 * 2`, allocates the payload, and restores nonblocking.
- `tube_poll`, `tube_wait`, and `tube_wait_timeout` use `poll`.
- Background reading uses a raw comm point and `tube_handle_listen`, which incrementally reads length and payload, then invokes the configured callback.
- Background writing uses `tube_queue_item` plus `tube_handle_write`, maintaining a FIFO list and partial-write offset.
- Delete removes event registrations, closes fds, frees partial command buffers and queued results.

Windows implementation:
- Uses an in-memory FIFO protected by `lock_basic_type` and signaled by a `WSAEVENT`.
- `tube_write_msg` duplicates the payload and queues it.
- `tube_read_msg` polls or waits on the event, pops one queued item, and resets the event when the queue becomes empty.
- Background listen registers the WSA event with the Unbound event layer; `tube_handle_signal` drains queued messages and invokes callbacks.
- There is no meaningful read fd on Windows; `tube_read_fd` returns `-1`.

Important integration points:
- Uses `util/netevent.h` comm points for async operation.
- Uses `util/ub_event.h` for Winsock event registration.
- Callback function pointers are checked through `fptr_wlist`.
- Direct read/write APIs should not be mixed with background listen/write APIs on the same tube.
