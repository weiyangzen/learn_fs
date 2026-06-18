# sources/test-tools/liburing/examples/echo-server.c

## sources/test-tools/liburing/examples/echo-server.c

Purpose: TCP echo server demonstrating modern io_uring networking with multishot accept, multishot receive, provided buffer rings, CQ ring sizing, and taskrun setup fallback.

Important APIs/types/functions: `struct conn`, `enum event_type`, global `ring`, `buf_ring`, `bufs`, `conns`; `encode_userdata`/decode helpers; `get_sqe`; `setup_buffer_ring`, `recycle_buffer`; `add_multishot_accept`, `add_recv`, `add_send`; handlers `handle_accept`, `handle_recv`, `handle_send`; `event_loop`; `setup_listening_socket` from helpers.

Control flow: main parses optional port, opens listening socket, initializes ring with `SUBMIT_ALL`, `CQSIZE`, `SINGLE_ISSUER`, `DEFER_TASKRUN` or fallback `COOP_TASKRUN`, registers provided buffers, arms accept, then loops over CQEs. Accept creates connection state and arms recv. Recv validates selected buffer, queues send, marks rearm when multishot stops or ENOBUFS occurs. Send recycles the buffer and rearms recv if needed.

State and persistence: persistent in-memory connection table indexed by fd, provided buffer ring, and heap buffer slab. Network sockets persist until closed; no files are written.

Dependencies/integration: requires liburing, helpers, kernel support for buffer rings and multishot recv, TCP sockets, and recent taskrun flags.

Risks: fd is packed into 16 bits and array-indexed; high fd values are rejected only above `MAX_CONNS`. Sends do not handle short positive sends for production. ENOBUFS recovery depends on send completions. No signal-driven shutdown path.

Test signals: manual `nc localhost 8000`; build coverage in examples; runtime kernel errors produce clear messages.
