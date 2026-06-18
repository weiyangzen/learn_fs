<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/fixed-buf-merge.c -->
## sources/test-tools/liburing/test/fixed-buf-merge.c

Purpose: regression test for fixed-buffer range merging/skipping when multiple fixed reads target adjacent offsets inside one registered buffer.

Important APIs/types/functions: `io_uring_register_buffers`, `io_uring_prep_read_fixed`, `io_uring_submit_and_wait`, `io_uring_for_each_cqe`, `io_uring_cq_advance`, and `t_aligned_alloc`.

Control flow: the test creates a temporary direct-IO file, allocates a large aligned buffer, registers it as one iovec, submits three fixed reads into consecutive 4096-byte slices starting at a 4096-byte offset inside the registered range, then checks all completions return 4096.

State and persistence behavior: one 128-page registered buffer backs several subrange fixed IOs. Temporary `.fixed-buf-*` file is unlinked on success and failure.

Dependencies and integration points: depends on O_DIRECT support and fixed-buffer registration over a larger range than each IO.

Risks: skips when O_DIRECT is unsupported. Failure indicates fixed-buffer accounting incorrectly merges or rejects subsegments.

Test signals: pass means fixed-buffer subrange lookup handles multiple adjacent requests inside one registered iovec.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/fixed-buf-merge.c -->
