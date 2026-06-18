# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_fiemap01.c

Purpose: `FS_IOC_FIEMAP` extent reporting for sparse file layout and expected extent flags. Source comment intent: Verify basic fiemap ioctl functionality, including: - The ioctl returns EBADR if it receives invalid fm_flags. - 0 extents are reported for an empty file. - The ioctl correctly retrieves single and multiple extent mappings after writing to the file..

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`; local functions `print_extens`, `check_extent_count`, `check_extent`, `verify_ioctl`, `setup`; key constants/macros `MNTPOINT`, `TESTFILE`, `NUM_EXTENT`; local structs `fiemap_extent`, `fiemap`, `statvfs`, `tst_test`; headers `linux/fs.h`, `linux/fiemap.h`, `stdlib.h`, `sys/statvfs.h`, `tst_test.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents.

State and persistence behavior: uses mounted test filesystems and file contents/extents as durable state, with cleanup removing opened files and mounts handled by LTP.

Dependencies and integration points: integrates with device- or procfs-specific ioctl contracts and errno behavior. Harness metadata `mount_device, needs_root, setup, skip_filesystems, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
