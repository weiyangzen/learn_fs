# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_getlbmd01.c

Purpose: `BLKGETLBMDCAPS` logical block metadata capability probing on block and regular-file fds. Source comment intent: Verify :manpage:`ioctl(2)` with FS_IOC_GETLBMD_CAP on block devices. - fill struct logical_block_metadata_cap with non-zero pattern, call FS_IOC_GETLBMD_CAP on a block device without integrity support and verify the kernel zeroed out all fields - call FS_IOC_GETLBMD_CAP on a regular file and verify it fails with ENOTTY.

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`; local functions `run`, `setup`, `cleanup`; local structs `logical_block_metadata_cap`, `tst_test`; headers `sys/ioctl.h`, `tst_test.h`, `lapi/fs.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: state is mostly transient file descriptor, process, or procfs/ioctl query data managed by the LTP harness.

Dependencies and integration points: integrates with device- or procfs-specific ioctl contracts and errno behavior. Harness metadata `bufs, cleanup, min_kver, needs_device, needs_kconfigs, needs_root, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
