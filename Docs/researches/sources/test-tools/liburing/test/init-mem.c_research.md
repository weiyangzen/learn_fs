<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/init-mem.c -->
## sources/test-tools/liburing/test/init-mem.c

Purpose: verifies `io_uring_queue_init_mem` and `io_uring_memory_size_params` compute sufficient memory for many SQ/CQ sizes and SQE/CQE layout variants.

Important APIs/types/functions: `struct ctx`, `struct q_entries`, `setup_ctx`, `check_red`, `test`, `io_uring_memory_size_params`, `io_uring_queue_init_mem`, `IORING_SETUP_CQSIZE`, `IORING_SETUP_NO_SQARRAY`, `IORING_SETUP_SQE128`, and `IORING_SETUP_CQE32`.

Control flow: for each entry configuration, the test allocates 2 MiB aligned memory, places redzones immediately before and after the ring memory region, initializes the ring in caller-provided memory, checks returned memory size matches the required size, then submits enough NOP batches to cycle through twice the CQ depth while repeatedly checking redzones and user_data ordering.

State and persistence behavior: ring memory is caller-owned and freed after `io_uring_queue_exit`. Redzone values detect overrun/underrun persistence.

Dependencies and integration points: covers custom ring memory initialization, no-SQ-array mode, CQ sizing, and 128-byte SQE/32-byte CQE modes.

Risks: unsupported parameters skip. A mismatch between size calculation and actual initialization is a serious memory corruption signal.

Test signals: pass means memory sizing is accurate and no ring operation writes outside the advertised buffer.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/init-mem.c -->
