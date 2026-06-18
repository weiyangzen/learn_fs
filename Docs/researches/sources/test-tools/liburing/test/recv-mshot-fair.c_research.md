# sources/test-tools/liburing/test/recv-mshot-fair.c

Purpose: tests fairness across multiple simultaneous multishot receive streams and validates the `optlen` byte limit for terminating a multishot request. It covers receive bundles and non-bundled multishot receive under defer-taskrun and cooperative task-run modes.

Important APIs and types: `io_uring_prep_recv_multishot`, SQE `optlen`, `IORING_RECVSEND_BUNDLE`, `IOSQE_BUFFER_SELECT`, `io_uring_setup_buf_ring`, pthread barriers, TCP loopback sockets, and CQE user data pointing to `struct recv_data`.

Control flow: `test()` prepares four receiver contexts on adjacent ports, starts one receiver thread that creates a CQ-sized ring and a 2048-entry buffer ring, and then runs four senders sequentially. `recv_prep()` binds/listens/accepts each connection, synchronizes with its sender, and arms a multishot receive. `do_recv()` waits for CQEs, attributes them to stream contexts via `io_uring_cqe_get_data()`, decrements remaining bytes, rearms when `MORE` is absent, and records unfairness if too many bytes arrive from one stream before switching. When `mshot_limit` is enabled, bytes since arm must not exceed `PER_MSHOT_LIMIT`. `run_tests()` executes bundled and non-bundled cases with and without the limit under defer and coop modes.

State and persistence: each `recv_data` records bytes remaining, bytes since arm, total bytes, unfair counters, and limit overshoot counters. Static `last_rd` and `bytes_since_last` track cross-stream scheduling fairness across CQEs.

Dependencies and integration: requires multishot iteration support, buffer rings, TCP loopback, and optionally `optlen` limit support. Unsupported iteration or limit support returns skip or pass depending on which feature is missing.

Risks and test signals: unfair scheduling, byte-limit overshoot, negative CQEs, missing buffer flags, or rearm failures fail. Passing indicates multishot receive does not monopolize one stream and honors per-request byte caps where supported.
