# sources/test-tools/liburing/examples/rsrc-update-bench.c

## sources/test-tools/liburing/examples/rsrc-update-bench.c

Purpose: Microbenchmark for sparse registered-file-table updates via io_uring.

Important APIs/functions: `io_uring_queue_init` with `SINGLE_ISSUER|DEFER_TASKRUN`, `io_uring_register_ring_fd`, `io_uring_register_files_sparse`, `io_uring_register_files_update`, `io_uring_prep_files_update`, `io_uring_submit`, `io_uring_wait_cqe`.

Control flow: create pipe, initialize ring, register ring fd and sparse table, prepopulate table entries by updating each index, then for 10 seconds queue batches of 32 file update operations at pseudo-random offsets, submit, wait for all completions, and count operations.

State and persistence: registered file table and pipe descriptors; no files.

Dependencies/integration: liburing resource registration/update APIs and pipe fds.

Risks: does not inspect CQE result values for each update, only wait errors. Random offset uses unbounded `rand()` modulo table size. Benchmark measures kernel update throughput but not correctness beyond API survival.

Test signals: stderr `max updates/s` throughput; failures on registration or submit.
