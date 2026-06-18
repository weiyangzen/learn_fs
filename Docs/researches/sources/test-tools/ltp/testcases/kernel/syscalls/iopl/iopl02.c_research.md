# sources/test-tools/ltp/testcases/kernel/syscalls/iopl/iopl02.c

Purpose: negative x86 `iopl` cases for level 4 EINVAL and unprivileged EPERM. Source comment intent: Copyright (c) Linux Test Project, 2020 Copyright (c) Wipro Technologies Ltd, 2002 Author: Subhab Biswas <subhabrata.biswas@wipro.com>.

Important APIs/types/functions: core calls `iopl`; local functions `verify_iopl`, `setup`, `cleanup`; local structs `tcase`, `passwd`, `tst_test`; headers `errno.h`, `unistd.h`, `pwd.h`, `tst_test.h`, `tst_safe_macros.h`, `sys/io.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: changes per-process I/O privilege state and restores it in cleanup where applicable.

Dependencies and integration points: integrates with x86 I/O privilege level changes and error handling. Harness metadata `cleanup, needs_root, setup, tcnt, test` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
