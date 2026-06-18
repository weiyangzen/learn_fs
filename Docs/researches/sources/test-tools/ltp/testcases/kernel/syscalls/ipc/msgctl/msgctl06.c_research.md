# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgctl/msgctl06.c

Purpose: `MSG_INFO`/`MSG_STAT_ANY` indexes and counts are cross-checked against `/proc/sysvipc/msg` as root and nobody. Source comment intent: Call msgctl() with MSG_INFO flag and check that: * The returned index points to a valid MSG by calling MSG_STAT_ANY * Also count that valid indexes < returned max index sums up to used_ids * And the data are consistent with /proc/sysvipc/msg There is a possible race between the call to the msgctl() and read from the proc file so this test cannot be run in parallel with any IPC testcases that adds or removes MSG queues. Note what we create a MSG segment in the test setup and send msg to make sure that there is at least one during the testrun. Also note that for MSG_INFO the members of the msginfo structure have completely different meaning than their names seems to suggest..

Important APIs/types/functions: core calls `msgctl`, `SAFE_MSGGET`, `SAFE_MSGCTL`, `SAFE_MSGSND`; local functions `parse_proc_sysvipc`, `verify_msgctl`, `setup`, `cleanup`; local structs `passwd`, `tcases`, `tcases`, `msqid_ds`, `msginfo`, `msqid_ds`, `buf`, `tst_test`; headers `stdio.h`, `pwd.h`, `tst_test.h`, `tst_safe_sysv_ipc.h`, `tse_newipc.h`, `lapi/msg.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with message queue metadata, permission, statistics, and time-field behavior. Harness metadata `cleanup, needs_root, setup, tcnt, test` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
