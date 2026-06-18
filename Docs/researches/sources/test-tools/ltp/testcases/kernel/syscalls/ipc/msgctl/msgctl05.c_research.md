# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgctl/msgctl05.c

Purpose: kernel clearing of msqid64 high time fields during `IPC_STAT`. Source comment intent: Cross verify the _high fields being set to 0 by the kernel..

Important APIs/types/functions: core calls `msgctl`, `SAFE_MSGGET`, `SAFE_MSGCTL`; local functions `run`; local structs `msqid64_ds`, `tst_test`; headers `sys/msg.h`, `lapi/msgbuf.h`, `tse_newipc.h`, `tst_test.h`, `tst_safe_sysv_ipc.h`.

Control flow: the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with message queue metadata, permission, statistics, and time-field behavior. Harness metadata `needs_tmpdir, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
