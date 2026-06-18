# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgget/msgget01.c

Purpose: queue creation followed by send/receive round trip for a generated IPC key. Source comment intent: Copyright (c) International Business Machines Corp., 2001.

Important APIs/types/functions: core calls `msgget`, `SAFE_MSGCTL`, `SAFE_MSGSND`, `SAFE_MSGRCV`; local functions `verify_msgget`, `setup`, `cleanup`; local structs `buf`, `tst_test`; headers `errno.h`, `string.h`, `sys/types.h`, `sys/ipc.h`, `sys/msg.h`, `tst_test.h`, `tst_safe_sysv_ipc.h`, `tse_newipc.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with queue allocation, key collisions, quota exhaustion, and checkpoint-restore next-id controls. Harness metadata `cleanup, needs_tmpdir, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
