# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify18.c

Purpose: validates unprivileged fanotify listener restrictions. It ensures disallowed init flags, disallowed mark scopes, and permission-event masks fail for an unprivileged process, while permitted unprivileged inode notification setup succeeds.

Important APIs/types/functions: `fanotify_init`, `fanotify_mark`, `FANOTIFY_REQUIRED_USER_INIT_FLAGS`, `FAN_UNLIMITED_QUEUE`, `FAN_UNLIMITED_MARKS`, `FAN_CLASS_CONTENT`, `FAN_CLASS_PRE_CONTENT`, `FAN_REPORT_TID`, `FAN_MARK_MOUNT`, `FAN_MARK_FILESYSTEM`, `FAN_ALL_EVENTS`, `FAN_ALL_PERM_EVENTS`, `SAFE_SETUID`, and `SAFE_GETPWNAM`.

Control flow: `setup()` creates a file on a mounted scratch filesystem, verifies fanotify fid support, drops from root to `nobody`, and confirms unprivileged fanotify is available. Each table case calls `fanotify_init`; expected `EPERM` on forbidden init flags passes. If initialization succeeds, it attempts `fanotify_mark` and expects `EPERM` for forbidden mount/filesystem marks or permission event masks, otherwise success is the expected result.

State/persistence behavior: only one test file and one notification fd are maintained. The process permanently drops uid during setup, so test state is mainly process credentials and the fanotify group lifetime until close.

Dependencies/integration: requires root initially to mount and then drop privileges, kernel support for unprivileged fanotify, and LTP fanotify constants that model required user init flags.

Risks/test signals: failure modes distinguish unsupported unprivileged fanotify (`TCONF`) from incorrect permission enforcement (`TFAIL` or `TBROK`). The test is sensitive to kernel policy changes around unprivileged fanotify.
