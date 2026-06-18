# sources/test-tools/liburing/test/link_drain.c

Purpose: stress-tests ordering when `IOSQE_IO_LINK` and `IOSQE_IO_DRAIN` are combined with normal writes and NOPs.

Important APIs/types/functions: `test_link_drain_one`, `test_link_drain_multi`, `test_drain`, `io_uring_prep_writev`, `io_uring_prep_nop`, `IOSQE_IO_LINK`, `IOSQE_IO_DRAIN`, `t_malloc`, and `t_probe_defer_taskrun`.

Control flow: the one-chain test submits write, linked NOP, linked drained NOP, NOP, and normal NOP, then expects CQEs in `user_data` order 0..4. The multi-chain test submits two linked/drained sequences and expects order 0..8. Each is repeated 1000 times for normal rings and, when supported, deferred taskrun rings.

State and persistence behavior: creates transient `testfile` files and unlinks/closes them. Tested state is scheduler ordering across link/drain dependencies.

Dependencies and integration points: integrates with filesystem writes, liburing helper allocation, and optional `IORING_SETUP_SINGLE_ISSUER | IORING_SETUP_DEFER_TASKRUN`.

Risks and test signals: any out-of-order completion, short submit, failed wait, or failure under deferred taskrun indicates broken drain/link sequencing.
