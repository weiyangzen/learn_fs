# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgget/msgget02.c

Purpose: `msgget` EEXIST, ENOENT, and EACCES cases with root and nobody execution paths. Source comment intent: Test for EEXIST, ENOENT, EACCES errors. - msgget(2) fails if a message queue exists for key and msgflg specified both IPC_CREAT and IPC_EXCL. - msgget(2) fails if no message queue exists for key and msgflg did not specify IPC_CREAT. - msgget(2) fails if a message queue exists for key, but the calling process does not have permission to access the queue, and does not have the CAP_IPC_OWNER capability..

Important APIs/types/functions: core calls `msgget`, `SAFE_MSGGET`, `SAFE_MSGCTL`; local functions `verify_msgget`, `do_test`, `setup`, `cleanup`; local structs `passwd`, `tcase`, `tcase`, `tst_test`; headers `errno.h`, `stdlib.h`, `sys/types.h`, `sys/ipc.h`, `sys/msg.h`, `pwd.h`, `tst_test.h`, `tst_safe_sysv_ipc.h`, `tse_newipc.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with queue allocation, key collisions, quota exhaustion, and checkpoint-restore next-id controls. Harness metadata `cleanup, forks_child, needs_root, needs_tmpdir, setup, tcnt, test` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
