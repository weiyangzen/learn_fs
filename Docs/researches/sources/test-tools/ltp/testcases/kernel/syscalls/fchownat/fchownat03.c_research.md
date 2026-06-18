# sources/test-tools/ltp/testcases/kernel/syscalls/fchownat/fchownat03.c

Purpose: negative `fchownat(2)` errno matrix covering access denial, bad fd, bad address, invalid flags, symlink loop, long path, missing path, non-directory fd, permission denial, and read-only filesystem.

Important APIs/types/functions: `fchownat`, `SAFE_TOUCH`, `SAFE_MKDIR`, `SAFE_OPEN`, `SAFE_SYMLINK`, `SAFE_SETEUID`, `tst_get_bad_addr`, LTP buffers, `.needs_rofs`, and errno constants `EACCES`, `EBADF`, `EFAULT`, `EINVAL`, `ELOOP`, `ENAMETOOLONG`, `ENOENT`, `ENOTDIR`, `EPERM`, `EROFS`.

Control flow: setup creates baseline files, opens the current directory, creates an inaccessible directory/file as root, drops to `nobody`, creates bad-address, regular-file fd, symlink loop, and long path state. Each table case calls `fchownat` with current euid/egid and expects the configured errno.

State/persistence behavior: combines credential state, rofs mount state, symlink loop state, and buffer-managed path strings. No ownership change should succeed.

Dependencies/integration: root, tempdir, read-only mount, and `nobody` account.

Risks/test signals: errno precedence is the main risk. The table isolates cases to make mismatches meaningful.
