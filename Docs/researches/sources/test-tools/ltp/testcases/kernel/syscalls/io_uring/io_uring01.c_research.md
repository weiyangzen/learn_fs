# sources/test-tools/ltp/testcases/kernel/syscalls/io_uring/io_uring01.c

Purpose: raw fixed-buffer read using `IORING_REGISTER_BUFFERS`, an SQE, `io_uring_enter`, and CQE data validation. Source comment intent: Copyright (C) 2020 ARM Ltd. All rights reserved. Author: Vikas Kumar <vikas.kumar2@arm.com> Copyright (C) 2020 Cyril Hrubis <chrubis@suse.cz> Tests for asynchronous I/O raw API i.e io_uring_setup(), io_uring_register() and io_uring_enter(). This tests validate basic API operation by creating a submission queue and a completion queue using io_uring_setup(). User buffer registered in the kernel for long term operation using io_uring_register(). This tests initiates I/O operations with the help of io_uring_enter()..

Important APIs/types/functions: core calls `io_uring_setup`, `io_uring_register`, `io_uring_enter`, `SAFE_OPEN`; local functions `setup_io_uring_test`, `check_buffer`, `drain_uring_cq`, `submit_to_uring_sq`, `cleanup_io_uring_test`, `run`, `setup`; key constants/macros `TEST_FILE`, `QUEUE_DEPTH`, `BLOCK_SZ`; local structs `tcase`, `io_uring_submit`, `iovec`, `io_cq_ring`, `io_uring_cqe`, `iovec`, `tcase`, `tst_test`; headers `io_uring_common.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents.

State and persistence behavior: maps ring buffers and may register fixed buffers; file, socket, RDS, and taint state are cleaned up after the test.

Dependencies and integration points: integrates with ring setup, registration, submission/completion queues, and kernel feature gating. Harness metadata `bufs, needs_tmpdir, save_restore, setup, tcnt, test` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
