# sources/test-tools/liburing/test/poll-race-mshot.c

Purpose: checks that racing socket wakeups do not reissue poll/multishot receive in ways that leak provided buffers or produce duplicate completions.

Important APIs/types/functions: `io_uring_setup_buf_ring`, `io_uring_prep_recv`, `io_uring_prep_recv_multishot`, `IOSQE_BUFFER_SELECT`, `IORING_CQE_F_BUFFER`, `IORING_CQE_F_MORE`, socketpair, pthread barrier, and `io_uring_free_buf_ring`.

Control flow: for 1000 loops, the regular test posts 64 receives using a provided buffer ring while another thread writes 64 buffers; every CQE must include a valid buffer id. Then for another 1000 loops, the multishot test arms one multishot receive with the same buffer ring and expects 64 data events plus terminal behavior or an explicit quieting path on kernels with `msg_inq` support.

State and persistence behavior: transient socketpairs, provided buffer rings, allocated receive buffers, and thread synchronization.

Dependencies and integration points: depends on buf-ring support, socket wakeups, and multishot recv behavior. `-EINVAL` buf-ring setup skips the whole test.

Risks and test signals: detects missing buffer ids, invalid buffer ids, too many CQEs, bad receive sizes, or multishot termination races that would leak buffers.
