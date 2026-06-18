# sources/test-tools/ltp/testcases/kernel/syscalls/ipc/semctl/semctl05.c

Purpose: `semctl` ERANGE for negative or too-large SETVAL/SETALL values. Source comment intent: Test for semctl() ERANGE error.

Important APIs/types/functions: core calls `semctl`, `SAFE_SEMGET`, `SAFE_SEMCTL`; local functions `verify_semctl`, `setup`, `cleanup`; key constants/macros `BIGV`; local structs `tcases`, `tcases`, `tst_test`; headers `tst_safe_sysv_ipc.h`, `tst_test.h`, `lapi/sem.h`, `tse_newipc.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates and removes SysV IPC objects whose ids, permissions, counters, timestamps, and queue/semaphore values are the state under test.

Dependencies and integration points: integrates with semaphore metadata, value arrays, permission checks, and concurrent semop stability. Harness metadata `cleanup, setup, tcnt, test` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: SysV IPC ids and sysctl-backed limits are shared host resources, so cleanup and nonparallel execution matter.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
