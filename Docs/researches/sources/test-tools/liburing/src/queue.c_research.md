<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/queue.c -->
## sources/test-tools/liburing/src/queue.c

Purpose: implements liburing's runtime queue operations: flushing SQEs, entering the kernel, waiting and peeking for CQEs, submitting with optional waits/timeouts, batch completion retrieval, and the exported `io_uring_get_sqe` symbol for ABI compatibility.

Important APIs/types/functions: core internals are `sq_ring_needs_enter`, `cq_ring_needs_flush`, `cq_ring_needs_enter`, `_io_uring_get_cqe`, `__io_uring_flush_sq`, `io_uring_wait_cqes_new`, `__io_uring_submit_timeout`, `__io_uring_submit_and_wait_timeout`, and `__io_uring_submit`. Public functions include `__io_uring_get_cqe`, `io_uring_get_events`, `io_uring_peek_batch_cqe`, `io_uring_wait_cqes`, `io_uring_wait_cqes_min_timeout`, `io_uring_submit_and_wait_reg`, `io_uring_submit_and_wait_timeout`, `io_uring_wait_cqe_timeout`, `io_uring_submit`, `io_uring_submit_and_wait`, `io_uring_submit_and_get_events`, and `__io_uring_sqring_wait`.

Control flow: submission begins by flushing local SQ state to kernel-visible tail. The code decides whether `io_uring_enter` is needed based on SQPOLL wakeup flags, CQ overflow/taskrun flags, wait requirements, and IOPOLL internal flags. Completion wait loops first peek locally, then enter the kernel if it must submit, wait, flush CQ overflow, or run task work. Timeouts use `IORING_ENTER_EXT_ARG` on newer kernels and an internal timeout SQE with `LIBURING_UDATA_TIMEOUT` on older kernels.

State and persistence behavior: mutates `sq.sqe_head`, `sq.sqe_tail`, `*sq.ktail`, `*cq.khead`, and uses `int_flags` and `features` to choose behavior. It also consumes internal timeout CQEs and skip CQEs so applications do not see them as normal completions.

Dependencies and integration points: depends on public inline helpers from `liburing.h`, memory barriers, syscall wrappers, `int_flags.h`, and sanitizer hooks. It is the central implementation behind application submit/wait calls.

Risks: subtle races exist around SQPOLL wakeup, CQ overflow, taskrun flags, registered wait offsets, mixed CQEs, and timeout CQE filtering. The code also warns that fallback timeout SQEs manipulate both SQ and CQ, making split producer/consumer threading unsafe on older kernels without synchronization.

Test signals: socket read/write tests, accept tests, timeout-link tests, registered wait tests, overflow tests, SQPOLL tests, and syzkaller reproductions stress this file. ASAN builds additionally validate SQE pointer fields before submit.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/queue.c -->
