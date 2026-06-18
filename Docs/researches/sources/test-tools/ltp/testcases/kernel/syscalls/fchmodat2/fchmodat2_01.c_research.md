# sources/test-tools/ltp/testcases/kernel/syscalls/fchmodat2/fchmodat2_01.c

Purpose: validates `fchmodat2(2)` on regular files, symlinks, and directories, including `AT_SYMLINK_NOFOLLOW` and `AT_EMPTY_PATH` behavior.

Important APIs/types/functions: `SAFE_FCHMODAT2`, raw `tst_syscall(__NR_fchmodat2)`, `SAFE_FSTATAT`, `AT_SYMLINK_NOFOLLOW`, `AT_EMPTY_PATH`, `O_PATH`, `SAFE_SYMLINKAT`, and all-filesystems LTP mount support.

Control flow: setup opens the mount directory with `O_PATH`, creates a directory, regular file, and symlink. `run()` tests regular-file chmod with and without nofollow, chmod via symlink target with flags zero, expected `EOPNOTSUPP` for nofollow symlink chmod, and `AT_EMPTY_PATH` chmod on an open directory fd.

State/persistence behavior: repeatedly changes file and directory modes and creates/removes a symlink and directory on each filesystem under test.

Dependencies/integration: root, formatted mounted device, all-filesystems matrix, LAPI fcntl/stat wrappers, and kernel behavior tagged to VFS blocking symlink nofollow chmod.

Risks/test signals: symlink mode behavior varies by filesystem/kernel support. The test expects symlink itself to remain `0777` and nofollow chmod to fail with `EOPNOTSUPP`.
