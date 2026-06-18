# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_pidfd.h

Purpose: targeted syscall behavior in the LTP kernel/syscalls suite. Source comment intent: SPDX-License-Identifier: GPL-2.0-or-later.

Important APIs/types/functions: core calls `ioctl`; local functions `ioctl_pidfd_get_info_supported`, `ioctl_pidfd_info_exit_supported`; key constants/macros `IOCTL_PIDFD_H`; local structs `pidfd_info`, `pidfd_info`; headers `tst_test.h`, `lapi/pidfd.h`.

Control flow: helper-only flow; callers invoke these inline wrappers from neighboring tests.

State and persistence behavior: state is mostly transient file descriptor, process, or procfs/ioctl query data managed by the LTP harness.

Dependencies and integration points: integrates with PIDFD_GET_INFO and process exit-status visibility across namespaces. Harness metadata `none explicit` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
