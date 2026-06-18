# sources/test-tools/ltp/testcases/kernel/syscalls/io_uring/io_uring_common.h

Purpose: shared raw-ring helper layer for mapping SQ/CQ rings, submitting read/write SQEs, and validating CQEs. Source comment intent: Copyright (C) 2026 IBM Author: Sachin Sant <sachinp@linux.ibm.com> Common definitions and helper functions for io_uring tests.

Important APIs/types/functions: core calls `io_uring_setup`, `io_uring_enter`; local functions `io_uring_setup_queue`, `io_uring_cleanup_queue`, `io_uring_submit_sqe_internal`, `io_uring_submit_sqe`, `io_uring_submit_sqe_vec`, `io_uring_wait_cqe`, `io_uring_init_buffer_pattern`, `io_uring_do_io_op`, `io_uring_do_vec_io_op`; key constants/macros `IO_URING_COMMON_H`; local structs `io_sq_ring`, `io_cq_ring`, `io_uring_cqe`, `io_uring_submit`, `io_sq_ring`, `io_uring_sqe`, `io_cq_ring`, `io_sq_ring`; headers `stdlib.h`, `string.h`, `fcntl.h`, `config.h`, `tst_test.h`, `lapi/io_uring.h`.

Control flow: helper-only flow; callers invoke these inline wrappers from neighboring tests.

State and persistence behavior: maps ring buffers and may register fixed buffers; file, socket, RDS, and taint state are cleaned up after the test.

Dependencies and integration points: integrates with ring setup, registration, submission/completion queues, and kernel feature gating. Harness metadata `none explicit` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
