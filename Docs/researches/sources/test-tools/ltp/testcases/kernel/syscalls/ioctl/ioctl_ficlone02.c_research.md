# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ficlone02.c

Purpose: `FICLONERANGE` whole-file clone with `file_clone_range` on mounted reflink filesystems. Source comment intent: This test verifies that :manpage:`ioctl(2)` FICLONE/FICLONERANGE feature correctly raises EOPNOTSUPP when an unsupported filesystem is used. In particular, filesystems which don't support copy-on-write..

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`; local functions `run`, `setup`; key constants/macros `MNTPOINT`, `SRCPATH`, `DSTPATH`; local structs `file_clone_range`, `stat`, `tst_test`; headers `tst_test.h`, `lapi/ficlone.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents.

State and persistence behavior: uses mounted test filesystems and file contents/extents as durable state, with cleanup removing opened files and mounts handled by LTP.

Dependencies and integration points: integrates with FICLONE/FICLONERANGE clone semantics on reflink-capable filesystems. Harness metadata `bufs, min_kver, mount_device, needs_root, setup, skip_filesystems, test_all, timeout` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
