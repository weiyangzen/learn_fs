# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/msgstress/msgstress01.c

Purpose: multi-process SysV message stress with paired writer/reader children and shared-memory result flags. Source comment intent: Stress test for SysV IPC. We send multiple messages at the same time, checking that we are not loosing any byte once we receive the messages from multiple children. The number of messages to send is determined by the free slots available in SysV IPC and the available number of children which can be spawned by the process. Each sender will spawn multiple messages at the same time and each receiver will read them one by one..

Important APIs/types/functions: core calls `msgrcv`, `msgsnd`, `SAFE_MSGGET`, `SAFE_MSGCTL`; local functions `get_used_sysvipc`, `reset_messages`, `create_message`, `writer`, `reader`, `remove_queues`, `run`, `setup`, `cleanup`; key constants/macros `SYSVIPC_TOTAL`, `SYSVIPC_USED`, `MSGTYPE`, `MAXNREPS`; local structs `sysv_msg`, `sysv_data`, `sysv_msg`, `sysv_data`, `sysv_data`, `sysv_data`, `sysv_msg`, `sysv_data`; headers `stdlib.h`, `tst_safe_sysv_ipc.h`, `tst_safe_stdio.h`, `tst_test.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with concurrent sender/receiver integrity under queue and process pressure. Harness metadata `cleanup, forks_child, options, runtime, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: This is stress/security-sensitive coverage and can expose kernel taint, crashes, or long runtimes on vulnerable or underprovisioned systems. SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
