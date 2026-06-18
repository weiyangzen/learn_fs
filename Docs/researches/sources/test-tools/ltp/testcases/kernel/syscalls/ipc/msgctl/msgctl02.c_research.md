# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgctl/msgctl02.c

Purpose: `IPC_SET` lowers `msg_qbytes` and restores original queue metadata. Source comment intent: Copyright (c) International Business Machines Corp., 2001 03/2001 - Written by Wayne Boyer Copyright (c) 2018 Cyril Hrubis <chrubis@suse.cz>.

Important APIs/types/functions: core calls `msgctl`, `SAFE_MSGGET`, `SAFE_MSGCTL`; local functions `verify_msgctl`, `setup`, `cleanup`; local structs `msqid_ds`, `msqid_ds`, `tst_test`; headers `errno.h`, `tst_test.h`, `tst_safe_sysv_ipc.h`, `tse_newipc.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with message queue metadata, permission, statistics, and time-field behavior. Harness metadata `cleanup, needs_tmpdir, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
