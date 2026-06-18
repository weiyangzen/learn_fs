<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/helpers.c -->
## sources/test-tools/liburing/test/helpers.c

Purpose: shared test utility implementation for allocation, file creation, ring setup, socket setup, timing, nonblocking toggles, submission helpers, and iovec comparison.

Important APIs/types/functions: `t_malloc`, `t_calloc`, `t_posix_memalign`, `t_aligned_alloc`, `t_create_file`, `t_create_file_pattern`, `t_create_buffers`, `t_create_ring_params`, `t_create_ring`, `t_register_buffers`, `t_create_socket_pair`, `t_create_socketpair_ip`, `t_probe_defer_taskrun`, `__io_uring_flush_sq`, `t_error`, timing helpers, `t_submit_and_wait_single`, `t_iovec_data_length`, and `t_compare_data_iovec`.

Control flow: functions are independent helpers. Most allocation helpers assert on failure; ring helpers normalize unsupported SQPOLL/invalid setup to `T_SETUP_SKIP`; socket helpers create connected IPv4/IPv6 TCP/UDP pairs; `__io_uring_flush_sq` publishes SQ tail with appropriate memory ordering.

State and persistence behavior: helpers create files, sockets, and rings on behalf of callers but generally transfer cleanup responsibility to tests. Timing helpers are pure calculations.

Dependencies and integration points: central dependency for almost all liburing tests, wrapping liburing APIs and Linux sockets/files.

Risks: assert-on-failure simplifies tests but aborts rather than returning recoverable errors. Incorrect `__io_uring_flush_sq` ordering would affect low-level SQPOLL/IOPOLL tests.

Test signals: this file is infrastructure; correctness is inferred by dependent tests using its helpers successfully.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/helpers.c -->
