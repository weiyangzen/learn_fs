<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/fixed-link.c -->
## sources/test-tools/liburing/test/fixed-link.c

Purpose: checks linked fixed-buffer reads use the current iovec lengths and complete successfully.

Important APIs/types/functions: `io_uring_register_buffers`, `io_uring_prep_read_fixed`, `io_uring_sqe_set_flags`, `IOSQE_IO_LINK`, and `/dev/zero`.

Control flow: the test opens `/dev/zero`, initializes a ring, allocates two 64-byte buffers, registers them, adjusts each iovec length to the length of a small string, queues two fixed reads linked together, submits and waits for both, and verifies each completion length matches the adjusted length.

State and persistence behavior: two registered buffers persist through the linked reads. Their `iov_len` fields are modified after registration in userspace, but the SQE read lengths are explicit.

Dependencies and integration points: exercises fixed buffer indexes, linked SQE submission, and completion validation.

Risks: no data comparison; it only checks result sizes. Cleanup is simple and early failures may leak allocations.

Test signals: pass indicates linked fixed reads complete with expected byte counts.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/fixed-link.c -->
