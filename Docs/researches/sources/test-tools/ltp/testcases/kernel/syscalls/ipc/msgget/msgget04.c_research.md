# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgget/msgget04.c

Purpose: `msg_next_id` desired identifier allocation and reset to -1 after successful queue creation. Source comment intent: It is a basic test for msg_next_id. msg_next_id specifies desired id for next allocated IPC message. By default it's equal to -1, which means generic allocation logic. Possible values to set are in range {0..INT_MAX}. The value will be set back to -1 by kernel after successful IPC object allocation..

Important APIs/types/functions: core calls `SAFE_MSGGET`, `SAFE_MSGCTL`; local functions `verify_msgget`, `setup`, `cleanup`; key constants/macros `NEXT_ID_PATH`; local structs `tst_test`; headers `errno.h`, `string.h`, `sys/types.h`, `sys/ipc.h`, `sys/msg.h`, `tst_test.h`, `tst_safe_sysv_ipc.h`, `tse_newipc.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with queue allocation, key collisions, quota exhaustion, and checkpoint-restore next-id controls. Harness metadata `cleanup, needs_kconfigs, needs_root, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
