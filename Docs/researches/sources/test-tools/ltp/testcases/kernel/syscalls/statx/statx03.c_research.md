<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx03.c

Purpose: Test basic error handling of statx syscall: - EBADF - Bad file descriptor - EFAULT - Bad address - EINVAL - Invalid argument - ENOENT - No such file or directory - ENOTDIR - Not a directory - ENAMETOOLONG - Filename too long

Important APIs/types/functions: includes `stdio.h`, `string.h`, `tst_test.h`, `tst_safe_macros.h`, `tst_get_bad_addr.h`, `lapi/stat.h`, `lapi/fcntl.h`; exercises `statx`, `syscall`; defines `run_test`, `setup`; uses constants `AT_FDCWD`, `EBADF`, `EFAULT`, `EINVAL`, `ENAMETOOLONG`, `ENOENT`, `ENOTDIR`, `O_CREAT`, `O_RDWR`.

Control flow centers on `run_test`, `setup`. The `struct tst_test` registration wires `.tcnt`, `.test`, `.setup`, `.needs_tmpdir` into the runner. Error-path expectations include `EBADF`, `EFAULT`, `EINVAL`, `ENAMETOOLONG`, `ENOENT`, `ENOTDIR`.

State and persistence behavior: Runtime state is filesystem metadata reported through `struct statx`: inode identity, size, timestamps, direct-I/O alignment, mount-root status, and attribute bits set by ioctls, fs-verity, encryption tooling, NFS cache state, or mounted filesystem support.

Dependencies and integration points: Depends on LTP safe file helpers, `lapi/stat.h`, `lapi/fcntl.h`, filesystem ioctl wrappers, mounted test devices, root privileges for attribute/mount cases, and feature probes for fs-verity, encryption, NFS, and DIO alignment. Direct include dependencies include `stdio.h`, `string.h`, `tst_test.h`, `tst_safe_macros.h`, `tst_get_bad_addr.h`, `lapi/stat.h`.

Risks and test signals: These tests are highly filesystem- and kernel-version-sensitive; unsupported attributes must be skipped or detected, and cleanup must restore inode flags and mounts. Test signals: reports through `TFAIL`, `TPASS`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EBADF`, `EFAULT`, `EINVAL`, `ENAMETOOLONG`, `ENOENT`, `ENOTDIR`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx03.c -->
