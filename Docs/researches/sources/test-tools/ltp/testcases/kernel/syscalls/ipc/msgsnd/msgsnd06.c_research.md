# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgsnd/msgsnd06.c

Purpose: blocking full-queue sender returns EIDRM when the queue is removed. Source comment intent: DESCRIPTION Tests if EIDRM is returned when message queue was removed while msgsnd() was trying to send a message..

Important APIs/types/functions: core calls `msgsnd`, `SAFE_MSGGET`, `SAFE_MSGCTL`; local functions `verify_msgsnd`, `do_test`, `setup`, `cleanup`; local structs `buf`, `tst_test`; headers `errno.h`, `unistd.h`, `sys/types.h`, `sys/ipc.h`, `sys/msg.h`, `tst_test.h`, `tst_safe_sysv_ipc.h`, `tse_newipc.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with enqueue behavior, full-queue blocking, permissions, and metadata updates. Harness metadata `cleanup, forks_child, needs_root, needs_tmpdir, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
