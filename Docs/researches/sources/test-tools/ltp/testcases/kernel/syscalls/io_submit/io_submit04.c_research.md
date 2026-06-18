# sources/test-tools/ltp/testcases/kernel/syscalls/io_submit/io_submit04.c

Purpose: `RWF_NOWAIT` read from an empty pipe through AIO, expecting a completion result of `-EAGAIN`. Source comment intent: Test RWF_NOWAIT support in io_submit(), verifying that an asynchronous read operation on a blocking resource (empty pipe) will cause -EAGAIN. This is done by checking that io_getevents() :manpage:`io_getevents(2)` syscall returns immediately and io_event.res is equal to -EAGAIN..

Important APIs/types/functions: core calls `io_getevents`, `io_submit`, `io_destroy`; local functions `setup`, `cleanup`, `run`; key constants/macros `BUF_SIZE`; local structs `io_event`, `timespec`, `tst_test`; headers `config.h`, `tst_test.h`, `lapi/syscalls.h`, `lapi/aio_abi.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates AIO contexts and temporary files/pipes, then destroys contexts and closes descriptors to avoid leaking kernel AIO state.

Dependencies and integration points: integrates with submission of raw or libaio `iocb` requests and completion harvesting. Harness metadata `bufs, cleanup, needs_kconfigs, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
