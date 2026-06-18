# sources/test-tools/liburing/test/mock_file.c

Purpose: integration tests for the `/dev/io_uring_mock` driver, covering mock-file creation, `uring_cmd` probing, registered-buffer copy commands, and mock read paths.

Important APIs/types/functions: `setup_mgr`, `create_mock_file`, `t_copy_regvec`, `t_copy_verify_regvec`, `test_regvec_cmd`, `test_rw`, `io_uring_prep_uring_cmd`, `IORING_URING_CMD_FIXED`, `io_uring_register_buffers`, and structs from `mock_file.h`.

Control flow: opens the mock manager device, probes feature bits, creates mock files, optionally runs registered-buffer copy commands in both directions over complex iovec layouts, and runs read tests over feature combinations of NOWAIT, async delay, and pollable mock files.

State and persistence behavior: uses global manager ring/fd and mock feature bitmap. Mock files are kernel/device objects returned as fds and closed after each test; no ordinary files are persisted.

Dependencies and integration points: requires `/dev/io_uring_mock`, sufficient permissions, liburing test helpers from `test.h`/`helpers.h`, and feature constants from `mock_file.h`.

Risks and test signals: skips when the mock device or feature is missing. Failures are probe/create command errors, copy length/data mismatches, unexpected read CQE sizes, or unsupported feature flags being mishandled.
