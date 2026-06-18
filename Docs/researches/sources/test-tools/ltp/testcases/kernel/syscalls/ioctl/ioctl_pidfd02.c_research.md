# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_pidfd02.c

Purpose: child exit-code retrieval via `PIDFD_INFO_EXIT` before and after reaping, with isolated and non-isolated children. Source comment intent: Copyright (c) 2025 Andrea Cervesato <andrea.cervesato@suse.com>.

Important APIs/types/functions: core calls `ioctl`, `SAFE_IOCTL`; local functions `run`, `setup`; local structs `tst_clone_args`, `pidfd_info`, `tst_test`; headers `ioctl_pidfd.h`, `lapi/sched.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents.

State and persistence behavior: state is mostly transient file descriptor, process, or procfs/ioctl query data managed by the LTP harness.

Dependencies and integration points: integrates with PIDFD_GET_INFO and process exit-status visibility across namespaces. Harness metadata `bufs, forks_child, needs_checkpoints, needs_kconfigs, setup, tcnt, test` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
