# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ns01.c

Purpose: `NS_GET_PARENT` EPERM behavior for the initial PID namespace and a new child PID namespace. Source comment intent: Copyright (c) 2019 Federico Bonfiglio <fedebonfi95@gmail.com> Copyright (c) Linux Test Project, 2019-2022.

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`; local functions `setup`, `cleanup`, `test_ns_get_parent`, `child`, `run`; key constants/macros `_GNU_SOURCE`, `STACK_SIZE`; local structs `tst_test`; headers `errno.h`, `stdlib.h`, `tst_test.h`, `lapi/ioctl_ns.h`, `lapi/sched.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: state is mostly transient file descriptor, process, or procfs/ioctl query data managed by the LTP harness.

Dependencies and integration points: integrates with namespace file-descriptor ioctls under `/proc/*/ns`. Harness metadata `cleanup, forks_child, min_kver, needs_root, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
