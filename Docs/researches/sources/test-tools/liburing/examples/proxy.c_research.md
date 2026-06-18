# sources/test-tools/liburing/examples/proxy.c

## sources/test-tools/liburing/examples/proxy.c

Purpose: Advanced TCP sink/proxy example demonstrating multishot accept/receive, per-connection rings and threads, fixed files, provided receive and send buffer rings, send/receive bundles, zerocopy send, NAPI, SQPOLL/DEFER_TASKRUN/COOP_TASKRUN, bidirectional forwarding, statistics, and graceful shutdown.

Important APIs/types/functions: global option/state variables; `struct conn`, `conn_dir`, `conn_buf_ring`, `io_msg`, `msg_vec`; buffer setup `setup_recv_ring`, `setup_send_ring`, `setup_send_zc`, `setup_buffer_rings`; event encoding from `proxy.h`; handlers `handle_accept`, `handle_sock`, `handle_connect`, `handle_recv`, `handle_send`, `handle_cancel`, `handle_shutdown`, `handle_close`, `handle_fd_pass`, `handle_stop`; event loops `parent_loop`, `__event_loop`; initialization `init_ring`; thread entry `thread_main`.

Control flow: main parses options, validates incompatible modes, adjusts recvmsg multishot buffer size, creates listening socket, installs stats/signal hooks, initializes parent ring, arms multishot accept, and enters parent loop. Each accepted connection spawns a thread with its own ring and buffer rings. Fixed-file mode passes accepted fd via `io_uring_prep_msg_ring_fd`; non-fixed mode stores fd directly. Proxy mode opens/connects outbound socket, then arms one or two receives. Receive CQEs move selected buffers into outgoing queues or recycle in sink mode. Send CQEs recycle buffers back to receive ring and may rearm receives. Shutdown is coordinated through cancels, shutdown/close chains, and parent housekeeping.

State and persistence: long-lived global connection table, per-connection rings, pthreads, provided buffer rings, optional huge page mappings, stats buckets, open sockets, and counters. No file persistence.

Dependencies/integration: liburing latest networking APIs, `helpers.c` socket setup, pthreads, Linux TCP, optional kernel features for fixed files, NAPI, send buffer select, bundles, zerocopy, huge pages.

Risks: intentionally experimental with many interacting modes. Several feature macros are locally defined pending upstream headers. Per-connection thread model caps at `MAX_CONNS` and relies on shared globals with limited locking. Bidirectional mode has TODOs around bid sequencing checks. Error handling often terminates a connection or process. Buffer accounting invariants are enforced with asserts, which can abort under unexpected kernel behavior.

Test signals: manual proxy/sink traffic, bandwidth and per-connection stats, CQ overflow logs, CI build coverage. Good runtime signals are no asserts, stable buffer counts, matching in/out bytes, and clean close stats.
