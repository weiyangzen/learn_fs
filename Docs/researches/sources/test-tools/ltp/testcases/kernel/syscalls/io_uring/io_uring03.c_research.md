# sources/test-tools/ltp/testcases/kernel/syscalls/io_uring/io_uring03.c

Purpose: basic `IORING_OP_WRITE` and `IORING_OP_READ` data-integrity tests including split writes. Source comment intent: Test IORING_OP_READ and IORING_OP_WRITE operations. This test validates basic read and write operations using io_uring. It tests: 1. IORING_OP_WRITE - Writing data to a file 2. IORING_OP_READ - Reading data from a file 3. Data integrity verification.

Important APIs/types/functions: core calls `SAFE_OPEN`; local functions `init_buffer`, `verify_data_integrity`, `test_write_read`, `test_partial_io`, `run`, `setup`, `cleanup`; key constants/macros `TEST_FILE`, `QUEUE_DEPTH`, `BLOCK_SZ`; local structs `io_uring_submit`, `tst_test`; headers `io_uring_common.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: maps ring buffers and may register fixed buffers; file, socket, RDS, and taint state are cleaned up after the test.

Dependencies and integration points: integrates with ring setup, registration, submission/completion queues, and kernel feature gating. Harness metadata `bufs, cleanup, needs_tmpdir, save_restore, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
