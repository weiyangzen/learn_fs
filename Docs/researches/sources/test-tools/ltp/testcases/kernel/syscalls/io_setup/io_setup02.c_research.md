# sources/test-tools/ltp/testcases/kernel/syscalls/io_setup/io_setup02.c

Purpose: raw `__NR_io_setup` coverage for EFAULT, EINVAL, EAGAIN, success, and matching `io_destroy` cleanup. Source comment intent: Test io_setup invoked via syscall(2): - io_setup fails and returns EFAULT if ctxp is NULL. - io_setup fails and returns EINVAL if ctxp is not initialized to 0. - io_setup fails and returns EINVAL if nr_events is -1. - io_setup fails and returns EAGAIN if nr_events exceeds the limit of available events. - io_setup succeeds if both nr_events and ctxp are valid..

Important APIs/types/functions: core calls `io_setup`; local functions `run`; local structs `tst_test`; headers `linux/aio_abi.h`, `config.h`, `tst_test.h`, `lapi/syscalls.h`.

Control flow: the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents.

State and persistence behavior: creates AIO contexts and temporary files/pipes, then destroys contexts and closes descriptors to avoid leaking kernel AIO state.

Dependencies and integration points: integrates with context allocation limits, invalid context pointers, and `/proc/sys/fs/aio-max-nr`. Harness metadata `needs_kconfigs, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
