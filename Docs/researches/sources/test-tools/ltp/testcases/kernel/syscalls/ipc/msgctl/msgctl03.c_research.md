# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgctl/msgctl03.c

Purpose: `IPC_RMID` removes a queue and subsequent `IPC_STAT` reports EINVAL. Source comment intent: DESCRIPTION msgctl13 - test for IPC_RMID.

Important APIs/types/functions: core calls `msgctl`, `SAFE_MSGGET`; local functions `verify_msgctl`; local structs `msqid_ds`, `tst_test`; headers `errno.h`, `tst_test.h`, `tst_safe_sysv_ipc.h`, `tse_newipc.h`.

Control flow: the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with message queue metadata, permission, statistics, and time-field behavior. Harness metadata `needs_tmpdir, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
