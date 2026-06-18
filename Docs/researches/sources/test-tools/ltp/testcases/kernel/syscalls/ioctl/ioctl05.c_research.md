# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl05.c

Purpose: block-device size consistency between `BLKGETSIZE` and `BLKGETSIZE64`, plus EOF behavior at device end. Source comment intent: Basic test for :manpage:`ioctl(2)` with BLKGETSIZE and BLKGETSIZE64. - BLKGETSIZE returns size in 512 byte blocks BLKGETSIZE64 in bytes compare that they return the same value. - lseek to the end of the device, this should work - try to read from the device, read should return 0.

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`, `SAFE_IOCTL`; local functions `verify_ioctl`, `cleanup`; local structs `tst_test`; headers `stdint.h`, `errno.h`, `sys/mount.h`, `tst_test.h`.

Control flow: the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: state is mostly transient file descriptor, process, or procfs/ioctl query data managed by the LTP harness.

Dependencies and integration points: integrates with device- or procfs-specific ioctl contracts and errno behavior. Harness metadata `cleanup, needs_device, needs_root, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Requires root and block-device/loop support; failures can reflect environment setup as well as kernel regressions.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
