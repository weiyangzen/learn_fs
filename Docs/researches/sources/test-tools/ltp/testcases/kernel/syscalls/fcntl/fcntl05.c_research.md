# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl05.c

Purpose: verifies `F_GETLK` reports `F_UNLCK` and preserves other `struct flock` fields when the requested lock would be placeable.

Important APIs/types/functions: `fcntl(fd, F_GETLK, &flocks)`, `struct flock`, `F_RDLCK`, `F_UNLCK`, `SEEK_CUR`, `SAFE_OPEN`, and `TST_EXP_EQ_LI`.

Control flow: setup opens a temp file and initializes `flocks` with `l_whence = SEEK_CUR`, zero start/len, and current pid. Each run resets `l_type` to `F_RDLCK`, calls `F_GETLK`, and checks `l_type` became `F_UNLCK` while whence/start/len/pid remain as initialized.

State/persistence behavior: no locks are placed. The only mutation is the kernel's update to the user `struct flock`.

Dependencies/integration: modern LTP tempdir test.

Risks/test signals: exact field-preservation expectations are the key. A kernel/libc ABI change to `F_GETLK` output fields would fail this test.
