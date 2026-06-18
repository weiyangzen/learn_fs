# sources/test-tools/ltp/testcases/kernel/syscalls/ioperm/ioperm02.c

Purpose: negative x86 `ioperm` cases for invalid high port ranges and unprivileged EPERM. Source comment intent: Copyright (c) Linux Test Project, 2020 Copyright (c) Wipro Technologies Ltd, 2002.

Important APIs/types/functions: core calls `ioperm`; local functions `setup`, `cleanup`, `verify_ioperm`; key constants/macros `NUM_BYTES`, `IO_BITMAP_BITS`, `IO_BITMAP_BITS_16`; local structs `tcase_t`, `passwd`, `tst_test`; headers `stdlib.h`, `errno.h`, `unistd.h`, `pwd.h`, `tst_test.h`, `tst_safe_macros.h`, `sys/io.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: changes per-process I/O privilege state and restores it in cleanup where applicable.

Dependencies and integration points: integrates with x86 I/O-port permission bitmap changes and privilege checks. Harness metadata `cleanup, needs_root, setup, tcnt, test` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
