# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgrcv/msgrcv07.c

Purpose: `MSG_EXCEPT`, `MSG_NOERROR`, `MSG_COPY`, and positive/zero/negative message type selection semantics. Source comment intent: Copyright (c) 2014-2020 Fujitsu Ltd. Author: Xiaoguang Wang <wangxg.fnst@cn.fujitsu.com> Author: Yang Xu <xuyang2018.jy@cn.fujitsu.com> Basic test for msgrcv(2) using MSG_EXCEPT, MSG_NOERROR, MSG_COPY and different msg_typ(zero,positive,negative). * With MSG_EXCEPT flag any message type but the one passed to the function is received. * With MSG_NOERROR and buffer size less than message size only part of the buffer is received. * With MSG_COPY and IPC_NOWAIT flag read the msg but don't destroy it in msg queue. * With msgtyp is 0, then the first message in the queue is read. * With msgtyp is greater than 0, then the first message in the queue of type msgtyp is read. * With msgtyp is less than .

Important APIs/types/functions: core calls `msgrcv`, `SAFE_MSGGET`, `SAFE_MSGCTL`, `SAFE_MSGSND`; local functions `prepare_queue`, `test_msg_except`, `test_msg_noerror`, `test_msg_copy`, `test_zero_msgtyp`, `test_positive_msgtyp`, `test_negative_msgtyp`, `cleanup`, `setup`, `verify_msgcrv`; key constants/macros `_GNU_SOURCE`, `MSGTYPE1`, `MSGTYPE2`, `MSG1`, `MSG2`; local structs `buf`, `msqid_ds`, `tst_test`; headers `sys/wait.h`, `tst_test.h`, `tst_safe_sysv_ipc.h`, `tse_newipc.h`, `lapi/msg.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with receive selection, blocking/error behavior, flags, and queue metadata updates. Harness metadata `cleanup, needs_tmpdir, setup, tcnt, test` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
