# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ficlone01.c

Purpose: whole-file reflink clone, inode/size/content checks, and copy-on-write isolation after destination modification. Source comment intent: This test verifies that :manpage:`ioctl(2)` FICLONE feature clones file content from one file to an another. [Algorithm] - populate source file - clone source content inside destination file - verify that source content has been cloned inside destination file - write a single byte inside destination file - verify that source content didn't change while destination did.

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`; local functions `run`, `cleanup`; key constants/macros `MNTPOINT`, `SRCPATH`, `DSTPATH`, `FILEDATA`, `FILESIZE`; local structs `stat`, `stat`, `tst_test`; headers `tst_test.h`, `lapi/ficlone.h`.

Control flow: the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: uses mounted test filesystems and file contents/extents as durable state, with cleanup removing opened files and mounts handled by LTP.

Dependencies and integration points: integrates with FICLONE/FICLONERANGE clone semantics on reflink-capable filesystems. Harness metadata `cleanup, filesystems, min_kver, mount_device, needs_root, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
