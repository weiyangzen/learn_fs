# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_pidfd01.c

Purpose: bad file descriptors for `PIDFD_GET_INFO` fail with allowed descriptor-specific errno values. Source comment intent: Verify that :manpage:`ioctl(2)` raises the right errors when an application provides wrong file descriptor..

Important APIs/types/functions: core calls `ioctl`; local functions `test_bad_pidfd`, `run`, `setup`; local structs `pidfd_info`, `tst_test`; headers `ioctl_pidfd.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents.

State and persistence behavior: state is mostly transient file descriptor, process, or procfs/ioctl query data managed by the LTP harness.

Dependencies and integration points: integrates with PIDFD_GET_INFO and process exit-status visibility across namespaces. Harness metadata `bufs, forks_child, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
