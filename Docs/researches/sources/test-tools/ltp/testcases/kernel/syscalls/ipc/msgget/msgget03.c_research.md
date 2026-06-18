# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgget/msgget03.c

Purpose: controlled `MSGMNI` exhaustion to force `msgget` ENOSPC, with sysctl save/restore. Source comment intent: Test for ENOSPC error. ENOSPC - All possible message queues have been taken (MSGMNI).

Important APIs/types/functions: core calls `msgget`, `SAFE_MSGCTL`; local functions `verify_msgget`, `setup`, `cleanup`; local structs `tst_test`; headers `errno.h`, `sys/types.h`, `sys/ipc.h`, `sys/msg.h`, `stdlib.h`, `tst_test.h`, `tst_safe_sysv_ipc.h`, `tse_newipc.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with queue allocation, key collisions, quota exhaustion, and checkpoint-restore next-id controls. Harness metadata `cleanup, needs_tmpdir, save_restore, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
