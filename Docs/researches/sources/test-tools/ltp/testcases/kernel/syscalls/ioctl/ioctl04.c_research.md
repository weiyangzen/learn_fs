# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl04.c

Purpose: block read-only state via `BLKROGET`/`BLKROSET`, verified by read-write and read-only mount attempts. Source comment intent: Basic test for :manpage:`ioctl(2)` with BLKROSET and BLKROGET . - Set the device read only, read the value back. - Try to mount the device read write, expect failure. - Try to mount the device read only, expect success..

Important APIs/types/functions: core calls `ioctl`, `mount`, `SAFE_OPEN`, `SAFE_IOCTL`; local functions `verify_ioctl`, `setup`, `cleanup`; local structs `tst_test`; headers `errno.h`, `sys/mount.h`, `tst_test.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: state is mostly transient file descriptor, process, or procfs/ioctl query data managed by the LTP harness.

Dependencies and integration points: integrates with device- or procfs-specific ioctl contracts and errno behavior. Harness metadata `cleanup, format_device, needs_root, setup, test_all, timeout` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Requires root and block-device/loop support; failures can reflect environment setup as well as kernel regressions.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
