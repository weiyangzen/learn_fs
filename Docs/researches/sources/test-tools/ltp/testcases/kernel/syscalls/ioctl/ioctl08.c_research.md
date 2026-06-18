# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl08.c

Purpose: btrfs `FIDEDUPERANGE` same/different/invalid-length cases and per-destination status validation. Source comment intent: Tests :manpage:`ioctl(2)` functionality to deduplicate fileranges using btrfs filesystem. 1. Sets the same contents for two files and deduplicates it. Deduplicates 3 bytes and set the status to FILE_DEDUPE_RANGE_SAME. 2. Sets different content for two files and tries to deduplicate it. 0 bytes get deduplicated and status is set to FILE_DEDUPE_RANGE_DIFFERS. 3. Sets same content for two files but sets the length to deduplicate to -1. ioctl(FIDEDUPERANGE) fails with EINVAL..

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`; local functions `verify_ioctl`, `cleanup`, `setup`; key constants/macros `SUCCESS`, `MNTPOINT`, `FILE_SRC_PATH`, `FILE_DEST_PATH`; local structs `file_dedupe_range`, `tcase`, `tcase`, `tst_test`; headers `config.h`, `stdlib.h`, `sys/ioctl.h`, `errno.h`, `tst_test.h`, `linux/fs.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: uses mounted test filesystems and file contents/extents as durable state, with cleanup removing opened files and mounts handled by LTP.

Dependencies and integration points: integrates with device- or procfs-specific ioctl contracts and errno behavior. Harness metadata `cleanup, filesystems, min_kver, mount_device, needs_root, setup, tcnt, test, timeout` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
