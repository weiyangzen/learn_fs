# sources/test-tools/liburing/test/poll-cancel-ton.c

Purpose: stress test for adding and removing very large numbers of poll requests by user-data identity.

Important APIs/types/functions: `POLL_COUNT=30000`, `sqe_index`, `io_uring_prep_poll_add`, `io_uring_prep_poll_remove`, `IORING_SETUP_CQSIZE`, `io_uring_peek_cqe`, and `io_uring_wait_cqe`.

Control flow: initializes a ring with large CQ when supported, batches 30,000 poll adds in chunks of 1024, storing SQE pointers as user data, then submits random poll remove batches and reaps up to twice each batch count.

State and persistence behavior: one pipe and the ring's large pending poll set are transient. `sqe_index` tracks cancellation keys.

Dependencies and integration points: depends on memory, CQ sizing support, and poll remove semantics. Falls back to normal ring if CQSIZE unsupported.

Risks and test signals: catches scalability issues, missed cancel completions, bad submit counts, and failure to handle large randomized cancel workloads.
