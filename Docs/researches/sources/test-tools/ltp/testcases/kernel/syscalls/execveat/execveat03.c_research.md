# sources/test-tools/ltp/testcases/kernel/syscalls/execveat/execveat03.c

Purpose: Regression test that an unlinked executable opened with `O_PATH` can still be executed by `execveat(..., AT_EMPTY_PATH)` on overlayfs.

Important APIs/types/functions: `SAFE_CP`, `SAFE_OPEN(... O_PATH)`, `SAFE_UNLINK`, `execveat`, `AT_EMPTY_PATH`, overlayfs mount support, and root-required LTP mount fields.

Control flow: The child copies the helper onto the overlay mount, opens it with `O_PATH`, unlinks it, and calls `execveat` by fd. A returned syscall is failure.

State and persistence behavior: The open file reference persists after unlink; overlay dentry/file capability lookup state is the regression target.

Dependencies and integration points: Requires root, a mounted overlayfs test device, `check_execveat()`, and the `execveat_child` helper.

Risks and test signals: Tagged for commits introducing and fixing the regression. Unsupported overlayfs or syscall support yields configuration skip rather than failure.
