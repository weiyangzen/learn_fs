# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl06.c

Purpose: block read-ahead round trips with `BLKRASET`/`BLKRAGET` and restoration of the original setting. Source comment intent: Basic test for :manpage:`ioctl(2)` with BLKRASET and BLKRAGET. Sets device read-ahead, reads it back and compares the values. The read-ahead value was choosen to be multiple of 512, since it's rounded based on page size on BLKRASET and 512 should be safe enough for everyone..

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`, `SAFE_IOCTL`; local functions `verify_ioctl`, `setup`, `cleanup`; local structs `tst_test`; headers `errno.h`, `sys/mount.h`, `tst_test.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: state is mostly transient file descriptor, process, or procfs/ioctl query data managed by the LTP harness.

Dependencies and integration points: integrates with device- or procfs-specific ioctl contracts and errno behavior. Harness metadata `cleanup, needs_device, needs_root, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Requires root and block-device/loop support; failures can reflect environment setup as well as kernel regressions.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
