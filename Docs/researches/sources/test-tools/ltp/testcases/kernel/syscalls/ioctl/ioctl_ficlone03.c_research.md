# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ficlone03.c

Purpose: negative `FICLONERANGE` cases covering invalid, read-only/write-only, directory, immutable, and mount file descriptors. Source comment intent: This test verifies that :manpage:`ioctl(2)` FICLONE/FICLONERANGE feature correctly raises exceptions when it's supposed to..

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`, `SAFE_IOCTL`; local functions `run`, `setup`, `cleanup`; key constants/macros `MNTPOINT`; local structs `file_clone_range`, `tcase`, `tcase`, `stat`, `tst_test`; headers `tst_test.h`, `lapi/ficlone.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: uses mounted test filesystems and file contents/extents as durable state, with cleanup removing opened files and mounts handled by LTP.

Dependencies and integration points: integrates with FICLONE/FICLONERANGE clone semantics on reflink-capable filesystems. Harness metadata `bufs, cleanup, filesystems, min_kver, mount_device, needs_root, setup, tcnt, test, timeout` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
