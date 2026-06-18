# sources/test-tools/ltp/testcases/kernel/syscalls/fchownat/fchownat02.c

Purpose: verifies `fchownat(2)` with `AT_SYMLINK_NOFOLLOW` changes symlink ownership rather than target ownership.

Important APIs/types/functions: `fchownat`, `SAFE_TOUCH`, `SAFE_SYMLINK`, `SAFE_STAT`, `SAFE_LSTAT`, `AT_SYMLINK_NOFOLLOW`, and `TST_EXP_EXPR`.

Control flow: setup creates a file and symlink, stats both target and link, and aborts if the link already has the target uid/gid expected for the test. The test calls `fchownat(AT_FDCWD, link, 1000, 1000, AT_SYMLINK_NOFOLLOW)`, then checks the target did not change while the link did.

State/persistence behavior: mutates symlink metadata only. The target file should retain original ownership.

Dependencies/integration: root, tempdir, and filesystem support for symlink ownership changes.

Risks/test signals: filesystems may have limited symlink ownership semantics. Failure is target ownership changed or link ownership not changed.
