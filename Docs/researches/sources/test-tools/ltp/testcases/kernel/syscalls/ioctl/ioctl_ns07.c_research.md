# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ns07.c

Purpose: namespace ioctl requests against non-namespace file descriptors returning ENOTTY. Source comment intent: Copyright (c) 2019 Federico Bonfiglio <fedebonfi95@gmail.com> Copyright (c) Linux Test Project, 2022.

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`; local functions `test_request`; key constants/macros `_GNU_SOURCE`; local structs `tst_test`; headers `errno.h`, `tst_test.h`, `lapi/ioctl_ns.h`.

Control flow: helper-only flow; callers invoke these inline wrappers from neighboring tests.

State and persistence behavior: state is mostly transient file descriptor, process, or procfs/ioctl query data managed by the LTP harness.

Dependencies and integration points: integrates with namespace file-descriptor ioctls under `/proc/*/ns`. Harness metadata `min_kver, needs_tmpdir, tcnt, test` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
