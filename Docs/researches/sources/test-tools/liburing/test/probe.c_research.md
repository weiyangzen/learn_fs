# sources/test-tools/liburing/test/probe.c

Purpose: validates `IORING_REGISTER_PROBE` and the liburing convenience probe helper. It checks that a partial probe reports metadata without operation entries and that a full probe marks core operations as supported.

Important APIs and types: `struct io_uring_probe`, `struct io_uring_probe_op`, `io_uring_register_probe`, `io_uring_get_probe_ring`, `io_uring_free_probe`, and opcode support flags such as `IO_URING_OP_SUPPORTED`. The expected operations include `IORING_OP_NOP`, `IORING_OP_READV`, and `IORING_OP_WRITE`.

Control flow: `test_probe()` allocates enough memory for 256 probe entries, first registers with count `0`, verifies `ops_len == 0` and nonzero `last_op`, then clears the buffer and registers for 256 entries, verifying the full table. `-EINVAL` from the first registration marks probe unsupported and sets `no_probe`. `test_probe_helper()` uses `io_uring_get_probe_ring()` and runs the same full verification. `main()` initializes a ring, runs direct probe, and only runs the helper if probing is supported.

State and persistence: `no_probe` records unsupported kernel behavior. Probe buffers are heap-allocated and freed after each path. No ring state is mutated besides registration queries.

Dependencies and integration: uses liburing's probe API and helpers for allocation and exit behavior. Extra argv skips the test for harness compatibility.

Risks and test signals: failures indicate malformed probe metadata, missing support bits for fundamental operations, or helper allocation/registration breakage. Unsupported kernels skip cleanly via `-EINVAL`; supported kernels must pass both direct and helper paths.
