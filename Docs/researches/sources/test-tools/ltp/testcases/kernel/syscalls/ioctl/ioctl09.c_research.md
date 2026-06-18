# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl09.c

Purpose: `BLKRRPART` partition reread on a loop device after `parted` modifies the partition table. Source comment intent: Basic test for :manpage:`ioctl(2)` with BLKRRPART, it is the same as blockdev --rereadpt command..

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`, `SAFE_IOCTL`; local functions `check_partition`, `verify_ioctl`, `setup`, `cleanup`; key constants/macros `RETVAL_CHECK`; local structs `loop_info`, `tst_test`; headers `stdio.h`, `unistd.h`, `string.h`, `sys/mount.h`, `stdbool.h`, `lapi/loop.h`, `tst_test.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: state is mostly transient file descriptor, process, or procfs/ioctl query data managed by the LTP harness.

Dependencies and integration points: integrates with device- or procfs-specific ioctl contracts and errno behavior. Harness metadata `cleanup, needs_cmds, needs_kconfigs, needs_root, needs_tmpdir, setup, test_all, timeout` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Requires root and block-device/loop support; failures can reflect environment setup as well as kernel regressions.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
