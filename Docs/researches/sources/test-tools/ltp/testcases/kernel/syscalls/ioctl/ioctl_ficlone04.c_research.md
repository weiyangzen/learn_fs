# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_ficlone04.c

Purpose: generic bad-fd matrix for `FICLONE` using LTP `tst_fd` descriptors. Source comment intent: This test verifies that :manpage:`ioctl(2)` FICLONE/FICLONERANGE feature raises the right error according with bad file descriptors..

Important APIs/types/functions: core calls `ioctl`; local functions `test_bad_fd`, `run`; local structs `tst_test`; headers `tst_test.h`, `lapi/ficlone.h`.

Control flow: the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents.

State and persistence behavior: uses mounted test filesystems and file contents/extents as durable state, with cleanup removing opened files and mounts handled by LTP.

Dependencies and integration points: integrates with FICLONE/FICLONERANGE clone semantics on reflink-capable filesystems. Harness metadata `min_kver, needs_root, needs_tmpdir, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
