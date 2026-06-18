# sources/test-tools/liburing/test/ringbuf-read.c

Purpose: tests mapped provided buffer rings with file reads, covering direct I/O, buffered I/O, and optional async submission.

Important APIs/types/functions: `io_uring_setup_buf_ring`, `io_uring_buf_ring_add`, `io_uring_buf_ring_advance`, `io_uring_prep_read`, `IOSQE_BUFFER_SELECT`, `IORING_CQE_F_BUFFER`, `IORING_CQE_BUFFER_SHIFT`, `O_DIRECT`, `posix_memalign`, and `posix_fadvise`.

Control flow: `main()` creates or uses a test file whose 128 blocks contain distinct byte patterns. `test()` sets up 128 provided buffers, queues reads for half the file with buffer selection, waits for completions, extracts selected buffer IDs, and verifies the chosen buffer contains the expected pattern for the request `user_data`. The matrix covers direct/buffered and sync/async unless buffer rings are unsupported.

State/persistence behavior: temporary file contents are deterministic block patterns; provided ring state tracks available buffers and selected IDs. The temporary file is unlinked unless provided by argv.

Dependencies/integration: uses liburing buffer-ring APIs, filesystem reads, alignment requirements for direct I/O, and helper `t_create_file`.

Risks/test signals: detects wrong buffer IDs, missing `IORING_CQE_F_BUFFER`, short reads, unsupported direct I/O, and stale/misrouted payload data. Resource cleanup is partial on some early failures, but test process exit bounds it.
