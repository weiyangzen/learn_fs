# sources/test-tools/liburing/test/defer.c

Purpose: tests drain/link/defer-style behavior around linked cancellation, timeouts, CQ overflow, and dropped SQ counters. Important APIs are `IOSQE_IO_LINK`, `IOSQE_IO_DRAIN`, `io_uring_prep_remove_buffers`, `io_uring_prep_timeout`, `io_uring_prep_link_timeout`, `ring.cq.koverflow`, `ring.sq.kdropped`, IOPOLL, and SQPOLL.

Control flow: build request contexts, verify linked NOP user_data, remove-buffer linked cancellations, drained linked timeouts, artificial overflow/dropped counters not hanging drained NOPs, and SQPOLL+IOPOLL linked remove-buffer cancellation. State is linked request chains and ring counters. Risks are hangs, wrong cancellation propagation, and user_data corruption.
