# sources/test-tools/ltp/testcases/kernel/syscalls/io_getevents/io_getevents02.c

Purpose: negative libaio coverage for an invalid zeroed AIO context; expected result is `-EINVAL`, not success or another negative libaio errno. Source comment intent: Test io_getevents invoked via libaio with invalid ctx and expects it to return -EINVAL..

Important APIs/types/functions: core calls `io_getevents`; local functions `run`; local structs `tst_test`; headers `config.h`, `tst_test.h`, `libaio.h`.

Control flow: the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents.

State and persistence behavior: creates AIO contexts and temporary files/pipes, then destroys contexts and closes descriptors to avoid leaking kernel AIO state.

Dependencies and integration points: integrates with the AIO completion wait path and libaio return-value conventions. Harness metadata `needs_kconfigs, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
