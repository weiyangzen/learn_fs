# File Research: sources/os/bsd/netbsd-src/lib/libisns/isns_task.c

Implements the libisns task dispatcher and queue operations. Task types include server discovery, reconnect, PDU send, socket I/O initialization, and refresh timer initialization.

Key behavior:
- `isns_run_task()` dispatches by task type through a static handler table.
- `isns_task_send_pdu()` converts PDU headers to network byte order, builds an iovec chain for header plus payload buffers, handles partial `writev()` progress, and processes connection loss on write failure.
- Waitable tasks use a condition variable and `wait_ref_count` so both the waiting caller and task completion path can release safely.
- Reconnect/init handlers manipulate sockets and kqueue events.
- Task queue helpers use `SIMPLEQ` protected by `cfg_p->taskq_mutex`.

Notable risks:
- `write_buf` is a static global buffer, so concurrent send handlers would conflict; current design appears to serialize through one control thread/current task.
- `isns_new_task()` callers assume allocation succeeds; some paths assign task fields without a NULL check.
