# sources/test-tools/liburing/test/msg-ring-overflow.c

Purpose: tests msg-ring delivery when the destination CQ is undersized and overflows.

Important APIs/types/functions: `io_uring_prep_msg_ring`, `IORING_SETUP_CQSIZE`, `IORING_SETUP_IOPOLL`, `IORING_SETUP_DEFER_TASKRUN`, `IORING_SETUP_SINGLE_ISSUER`, and `io_uring_wait_cqe`.

Control flow: creates a destination ring with four CQ entries, submits eight msg-ring SQEs from a source ring, then drains eight sender completions and eight destination CQEs. The matrix includes normal, IOPOLL, deferred, and deferred+IOPOLL destination flags.

State and persistence behavior: transient CQ overflow/overflow flushing state. No files.

Dependencies and integration points: depends on msg-ring support, CQ size override support, and destination ring modes.

Risks and test signals: detects lost messages, bad len/user_data in overflowed destination CQEs, sender completion errors, and old kernels where only one SQE submits or returns unsupported status.
