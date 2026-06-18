<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/iopoll-overflow.c -->
## sources/test-tools/liburing/test/iopoll-overflow.c

Purpose: stresses IOPOLL completion queue overflow handling with many submitted direct reads and a small CQ size.

Important APIs/types/functions: `test`, `t_create_ring_params`, `IORING_SETUP_IOPOLL`, `IORING_SETUP_CQSIZE`, `IORING_SETUP_SUBMIT_ALL`, raw `__sys_io_uring_enter`, `io_uring_prep_read`, and `io_uring_wait_cqe`.

Control flow: the ring is created with 64 SQ entries and 64 CQ entries, then eight batches of 32 reads are submitted without reaping completions. After a short sleep, the test enters the kernel requesting all 256 events and then waits/reaps each CQE.

State and persistence behavior: global `vecs` hold aligned buffers, and the CQ is intentionally overfilled relative to its configured size. Temporary file is removed when created by the test.

Dependencies and integration points: requires O_DIRECT and IOPOLL support.

Risks: unsupported filesystems skip. It does not validate each `cqe->res`, focusing on overflow/liveness.

Test signals: pass means IOPOLL CQ overflow can be drained without lost wakeups or hangs.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/iopoll-overflow.c -->
