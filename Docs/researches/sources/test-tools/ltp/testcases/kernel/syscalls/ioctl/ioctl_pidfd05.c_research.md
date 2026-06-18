# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_pidfd05.c

Purpose: NULL and short extensible `PIDFD_GET_INFO` arguments fail with EINVAL or ENOTTY depending on kernel validation. Source comment intent: Verify that :manpage:`ioctl(2)` raises an EINVAL or ENOTTY (since v6.18-rc1) error when PIDFD_GET_INFO is used. This happens when: - info parameter is NULL - info parameter is providing the wrong size.

Important APIs/types/functions: core calls `ioctl`; local functions `run`, `setup`; key constants/macros `PIDFD_GET_INFO_SHORT`; local structs `pidfd_info_invalid`, `tst_clone_args`, `pidfd_info_invalid`, `tst_test`; headers `tst_test.h`, `lapi/pidfd.h`, `lapi/sched.h`, `errno.h`, `ioctl_pidfd.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents.

State and persistence behavior: state is mostly transient file descriptor, process, or procfs/ioctl query data managed by the LTP harness.

Dependencies and integration points: integrates with PIDFD_GET_INFO and process exit-status visibility across namespaces. Harness metadata `bufs, forks_child, needs_kconfigs, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
