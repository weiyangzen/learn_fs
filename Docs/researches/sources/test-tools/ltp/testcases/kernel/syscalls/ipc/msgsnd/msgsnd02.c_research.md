# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgsnd/msgsnd02.c

Purpose: send error matrix for EACCES, EFAULT, EINVAL queue id, non-positive types, and negative size. Source comment intent: DESCRIPTION 1) The calling process does not have write permission on the message queue, so msgsnd(2) fails and sets errno to EACCES. 2) msgsnd(2) fails and sets errno to EFAULT if the message buffer address is invalid. 3) msgsnd(2) fails and sets errno to EINVAL if the queue ID is invalid. 4) msgsnd(2) fails and sets errno to EINVAL if the message type is not positive (0). 5) msgsnd(2) fails and sets errno to EINVAL if the message type is not positive (>0). 6) msgsnd(2) fails and sets errno to EINVAL if the message size is less than zero..

Important APIs/types/functions: core calls `msgsnd`, `SAFE_MSGGET`, `SAFE_MSGCTL`; local functions `verify_msgsnd`, `do_test`, `setup`, `cleanup`; local structs `passwd`, `buf`, `tcase`, `buf`, `tcase`, `tst_test`; headers `errno.h`, `string.h`, `stdlib.h`, `sys/types.h`, `sys/ipc.h`, `sys/msg.h`, `pwd.h`, `tst_test.h`, `tst_safe_sysv_ipc.h`, `tse_newipc.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with enqueue behavior, full-queue blocking, permissions, and metadata updates. Harness metadata `cleanup, forks_child, needs_root, needs_tmpdir, setup, tcnt, test` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
