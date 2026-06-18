# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgctl/msgctl04.c

Purpose: message-control EACCES/EFAULT/EINVAL/EPERM matrix across libc and raw syscall variants. Source comment intent: Test for EACCES, EFAULT and EINVAL errors using a variety of incorrect calls..

Important APIs/types/functions: core calls `msgctl`, `SAFE_MSGGET`, `SAFE_MSGCTL`; local functions `libc_msgctl`, `sys_msgctl`, `verify_msgctl`, `setup`, `cleanup`; local structs `msqid_ds`, `tcase`, `msqid_ds`, `test_variants`, `test_variants`, `test_variants`, `passwd`, `tst_test`; headers `errno.h`, `pwd.h`, `tst_test.h`, `tst_safe_sysv_ipc.h`, `tse_newipc.h`, `lapi/syscalls.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with message queue metadata, permission, statistics, and time-field behavior. Harness metadata `cleanup, needs_root, needs_tmpdir, setup, tcnt, test, test_variants` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter. Variant coverage depends on syscall availability and kernel time ABI support.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
