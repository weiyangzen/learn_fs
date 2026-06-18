# sources/test-tools/ltp/testcases/kernel/syscalls/io_submit/io_submit02.c

Purpose: raw syscall success cases where `io_submit` returns the submitted count or zero for `nr == 0`. Source comment intent: Test io_submit invoked via syscall(2): 1. io_submit() returns the number of iocbs submitted. 2. io_submit() returns 0 if nr is zero..

Important APIs/types/functions: core calls `io_submit`, `io_destroy`, `SAFE_OPEN`; local functions `io_prep_option`, `setup`, `cleanup`, `run`; key constants/macros `TEST_FILE`, `MODE`; local structs `iocb`, `iocb`, `tcase`, `iocb`, `io_event`, `timespec`, `tst_test`; headers `linux/aio_abi.h`, `config.h`, `tst_test.h`, `lapi/syscalls.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates AIO contexts and temporary files/pipes, then destroys contexts and closes descriptors to avoid leaking kernel AIO state.

Dependencies and integration points: integrates with submission of raw or libaio `iocb` requests and completion harvesting. Harness metadata `cleanup, needs_kconfigs, needs_tmpdir, setup, tcnt, test` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
