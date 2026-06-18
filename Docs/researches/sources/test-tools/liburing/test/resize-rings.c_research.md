# sources/test-tools/liburing/test/resize-rings.c

Purpose: stress-tests `io_uring_resize_rings()` across normal, async, SQPOLL, and `SINGLE_ISSUER|DEFER_TASKRUN` rings while requests and CQEs are in flight. It targets SQ/CQ remapping correctness, CQE preservation, overflow rejection, and mmap races.

Important APIs/types/functions: `io_uring_resize_rings`, `io_uring_queue_init_params`, `io_uring_queue_mmap`, `io_uring_unmap_rings`, `io_uring_for_each_cqe`, `io_uring_cq_advance`, `io_uring_prep_read`, `io_uring_prep_nop`, `IOSQE_ASYNC`, `IORING_SETUP_SQPOLL`, `IORING_SETUP_SINGLE_ISSUER`, and `IORING_SETUP_DEFER_TASKRUN`.

Control flow: `main()` optionally opens `/dev/nvme0n1` for direct read coverage, then runs `test()` over several ring modes and async settings. `test_basic()` verifies a NOP before and after resize, `test_reads()` and `test_pipes()` resize while blocking reads complete, `test_all_copy()` verifies CQE order after growing, `test_overflow()` expects `-EOVERFLOW` when shrinking below pending CQEs, `test_same_resize()` checks same-size resize, and `test_mmap_race()` forks children that mmap/unmap the ring while the parent resizes.

State/persistence behavior: no durable state except optional device/file reads; most state is ring mapping metadata, pending SQEs/CQEs, pipe bytes, per-request `user_data`, and child mmap views. The pipe writer thread creates live completions while the ring shape changes.

Dependencies/integration: uses liburing helpers, pthreads, fork/wait, pipes, optional block device direct I/O, and kernel support for resize and deferred taskrun. Unsupported setup or resize support is surfaced as `T_EXIT_SKIP`.

Risks/test signals: failures include lost/misordered CQEs, bad `user_data`, negative read CQEs, unexpected resize errors, overflow not rejected, or crash/race symptoms. The mmap race is timing-sensitive and intentionally stress-oriented.
