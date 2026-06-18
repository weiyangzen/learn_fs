# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgrcv/msgrcv02.c

Purpose: receive error matrix for E2BIG, EACCES, EFAULT, EINVAL, and ENOMSG. Source comment intent: Copyright (c) International Business Machines Corp., 2001 Basic error test for msgrcv(2). 1)msgrcv(2) fails and sets errno to E2BIG if the message text length is greater than msgsz and MSG_NOERROR isn't specified in msgflg. 2)The calling process does not have read permission on the message queue, so msgrcv(2) fails and sets errno to EACCES. 3)msgrcv(2) fails and sets errno to EFAULT if the message buffer address isn't accessible. 4)msgrcv(2) fails and sets errno to EINVAL if msqid was invalid(<0). 5)msgrcv(2) fails and sets errno to EINVAL if msgsize is less than 0. 6)msgrcv(2) fails and sets errno to ENOMSG if IPC_NOWAIT was specified in msgflg and no message of the requested type existed o.

Important APIs/types/functions: core calls `msgrcv`, `SAFE_MSGGET`, `SAFE_MSGCTL`, `SAFE_MSGSND`; local functions `verify_msgrcv`, `do_test`, `setup`, `cleanup`; key constants/macros `_GNU_SOURCE`; local structs `passwd`, `buf`, `tcase`, `buf`, `tcase`, `tst_test`; headers `string.h`, `sys/wait.h`, `sys/msg.h`, `stdlib.h`, `pwd.h`, `tst_test.h`, `tst_safe_sysv_ipc.h`, `tse_newipc.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with receive selection, blocking/error behavior, flags, and queue metadata updates. Harness metadata `cleanup, forks_child, needs_root, needs_tmpdir, setup, tcnt, test` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
