# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgrcv/msgrcv08.c

Purpose: compat regression for negative `msgtyp` receive selecting the expected positive message type. Source comment intent: Copyright (c) 2015 Author: Gabriellla Schmidt <gsc@bruker.de> Modify: Li Wang <liwang@redhat.com> A regression test for: commit e7ca2552369c1dfe0216c626baf82c3d83ec36bb Author: Mateusz Guzik <mguzik@redhat.com> Date: Mon Jan 27 17:07:11 2014 -0800 ipc: fix compat msgrcv with negative msgtyp Reproduce: 32-bit application using the msgrcv() system call gives the error message: msgrcv: No message of desired type If this progarm is compiled as 64-bit application it works..

Important APIs/types/functions: core calls `msgrcv`, `SAFE_MSGGET`, `SAFE_MSGCTL`, `SAFE_MSGSND`; local functions `verify_msgrcv`, `setup`, `cleanup`; local structs `mbuf`, `tst_test`; headers `stdio.h`, `string.h`, `unistd.h`, `sys/types.h`, `sys/ipc.h`, `sys/msg.h`, `tst_test.h`, `tst_safe_sysv_ipc.h`, `tse_newipc.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with receive selection, blocking/error behavior, flags, and queue metadata updates. Harness metadata `cleanup, needs_tmpdir, setup, tags, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
