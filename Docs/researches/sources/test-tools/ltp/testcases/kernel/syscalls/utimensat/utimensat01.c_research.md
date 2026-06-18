<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utimensat/utimensat01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/utimensat/utimensat01.c

Purpose: broad `utimensat()` ABI and permission test covering read-only/writable files, append-only and immutable inode flags, `UTIME_NOW`, `UTIME_OMIT`, explicit timestamps, bad addresses, bad dirfd/path combinations, and old/time64 syscall variants.

Important APIs/types/functions: `tcase[]` encodes dirfd, pathname, synthetic time tuple, flags, open flags, inode attributes, mode, and expected errno. `variants[]` selects `__NR_utimensat` or `__NR_utimensat_time64`. `multi_set_time()` fills libc/old-kernel/time64 timespec unions. `update_error()` normalizes immutable-file errno across kernel versions. `change_attr()` uses `FS_IOC_GETFLAGS/SETFLAGS`. `reset_time()` resets timestamps before each case. `run()` orchestrates per-case setup, syscall, attribute cleanup, and stat validation.

Control flow/state: every case opens/creates the target if needed, resets times to zero, applies requested inode flags, calls the selected ABI, removes flags, then either checks errno or verifies atime/mtime changed exactly according to `mytime` flags. Persistent state includes `mntpoint/test_file`, `mntpoint/test_dir`, and transient inode flags.

Dependencies/integration: depends on LTP time64 helpers, `lapi/fs.h`, `lapi/utime.h`, root, and a mounted filesystem that supports tested attributes. `ENOTTY` on flag ioctls is treated as `TCONF`.

Risks/test signals: this test is sensitive to kernel version errno changes, filesystem support for immutable/append flags, and timestamp truthiness because success validation expects zero/nonzero changes after reset. Variant-specific failures isolate old-timespec versus time64 ABI regressions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utimensat/utimensat01.c -->
