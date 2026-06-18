# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgrcv/msgrcv03.c

Purpose: invalid `MSG_COPY` flag combinations and out-of-range copy index behavior. Source comment intent: Copyright (c) 2020 FUJITSU LIMITED. All rights reserved. Author: Yang Xu <xuyang2018.jy@cn.jujitsu.com> This is a basic test about MSG_COPY flag. This flag was added in 3.8 for the implementation of the kernel checkpoint restore facility and is available only if the kernel was built with the CONFIG_CHECKPOINT_RESTORE option. On old kernel without this support, it only ignores this flag and doesn't report ENOSYS/EINVAL error. The CONFIG_CHECKPOINT_RESTORE has existed before kernel 3.8. So for using this flag, kernel should greater than 3.8 and enable CONFIG_CHECKPOINT_RESTORE together. 1)msgrcv(2) fails and sets errno to EINVAL if IPC_NOWAIT was not specified in msgflag. 2)msgrcv(2) fails and.

Important APIs/types/functions: core calls `msgrcv`, `SAFE_MSGGET`, `SAFE_MSGCTL`, `SAFE_MSGSND`; local functions `verify_msgrcv`, `setup`, `cleanup`; key constants/macros `_GNU_SOURCE`; local structs `buf`, `tcase`, `tcase`, `tst_test`; headers `string.h`, `sys/wait.h`, `pwd.h`, `tst_test.h`, `tst_safe_sysv_ipc.h`, `tse_newipc.h`, `lapi/msg.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with receive selection, blocking/error behavior, flags, and queue metadata updates. Harness metadata `cleanup, needs_kconfigs, needs_root, needs_tmpdir, setup, tcnt, test` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
