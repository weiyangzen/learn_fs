<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx02.c

Purpose: This code tests the following flags with statx syscall: - AT_EMPTY_PATH - AT_SYMLINK_NOFOLLOW A test file and a link for it is created. To check empty path flag, test file fd alone is passed. Predefined size of testfile is checked against obtained value. To check symlink no follow flag, the linkname is statxed. To ensure that link is not dereferenced, obtained inode is compared with test file inode.

Important APIs/types/functions: includes `stdio.h`, `inttypes.h`, `tst_test.h`, `tst_safe_macros.h`, `lapi/stat.h`, `lapi/fcntl.h`; exercises `statx`, `symlink`, `syscall`; defines `test_empty_path`, `test_sym_link`, `run`, `setup`, `cleanup`; uses constants `AT_EMPTY_PATH`, `AT_FDCWD`, `AT_SYMLINK_NOFOLLOW`, `O_CREAT`, `O_RDWR`.

Control flow centers on `test_empty_path`, `test_sym_link`, `run`, `setup`, `cleanup`. The `struct tst_test` registration wires `.test`, `.tcnt`, `.setup`, `.cleanup`, `.needs_tmpdir` into the runner.

State and persistence behavior: Runtime state is filesystem metadata reported through `struct statx`: inode identity, size, timestamps, direct-I/O alignment, mount-root status, and attribute bits set by ioctls, fs-verity, encryption tooling, NFS cache state, or mounted filesystem support.

Dependencies and integration points: Depends on LTP safe file helpers, `lapi/stat.h`, `lapi/fcntl.h`, filesystem ioctl wrappers, mounted test devices, root privileges for attribute/mount cases, and feature probes for fs-verity, encryption, NFS, and DIO alignment. Direct include dependencies include `stdio.h`, `inttypes.h`, `tst_test.h`, `tst_safe_macros.h`, `lapi/stat.h`, `lapi/fcntl.h`.

Risks and test signals: These tests are highly filesystem- and kernel-version-sensitive; unsupported attributes must be skipped or detected, and cleanup must restore inode flags and mounts. Test signals: reports through `TFAIL`, `TPASS`, `TST_RET`, `TTERRNO`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx02.c -->
