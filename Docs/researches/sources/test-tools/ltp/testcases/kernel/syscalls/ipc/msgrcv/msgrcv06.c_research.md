# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgrcv/msgrcv06.c

Purpose: blocking `msgrcv` returns EIDRM when the queue is removed while the child sleeps. Source comment intent: Copyright (c) International Business Machines Corp., 2001 msgrcv error test for EIDRM..

Important APIs/types/functions: core calls `msgrcv`, `SAFE_MSGGET`, `SAFE_MSGCTL`; local functions `verify_msgrcv`, `do_test`, `setup`, `cleanup`; local structs `buf`, `tst_test`; headers `errno.h`, `unistd.h`, `sys/types.h`, `sys/ipc.h`, `sys/msg.h`, `stdlib.h`, `tst_test.h`, `tst_safe_sysv_ipc.h`, `tse_newipc.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with receive selection, blocking/error behavior, flags, and queue metadata updates. Harness metadata `cleanup, forks_child, needs_tmpdir, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
