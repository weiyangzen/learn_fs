<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx05.c

Purpose: Test statx syscall with STATX_ATTR_ENCRYPTED flag, setting a key is required for the file to be encrypted by the filesystem. e4crypt is used to set the encrypt flag (currently supported only by ext4). Two directories are tested. First directory has all flags set. Second directory has no flags set. Minimum e2fsprogs version required is 1.43.

Important APIs/types/functions: includes `stdlib.h`, `stdio.h`, `sys/types.h`, `sys/wait.h`, `tst_test.h`, `lapi/fs.h`, `lapi/stat.h`, `lapi/fcntl.h`; exercises `statx`, `syscall`; defines `test_flagged`, `test_unflagged`, `run`, `setup`, `cleanup`; uses constants `AT_FDCWD`, `STATX_ATTR_ENCRYPTED`.

Control flow centers on `test_flagged`, `test_unflagged`, `run`, `setup`, `cleanup`. The `struct tst_test` registration wires `.test`, `.tcnt`, `.setup`, `.cleanup`, `.needs_root`, `.needs_device`, `.mntpoint`, `.filesystems`, `.needs_cmds` into the runner. Named case hints include `-O encrypt`.

State and persistence behavior: Runtime state is filesystem metadata reported through `struct statx`: inode identity, size, timestamps, direct-I/O alignment, mount-root status, and attribute bits set by ioctls, fs-verity, encryption tooling, NFS cache state, or mounted filesystem support.

Dependencies and integration points: Depends on LTP safe file helpers, `lapi/stat.h`, `lapi/fcntl.h`, filesystem ioctl wrappers, mounted test devices, root privileges for attribute/mount cases, and feature probes for fs-verity, encryption, NFS, and DIO alignment. Direct include dependencies include `stdlib.h`, `stdio.h`, `sys/types.h`, `sys/wait.h`, `tst_test.h`, `lapi/fs.h`.

Risks and test signals: These tests are highly filesystem- and kernel-version-sensitive; unsupported attributes must be skipped or detected, and cleanup must restore inode flags and mounts. Test signals: reports through `TCONF`, `TFAIL`, `TPASS`, `TST_RET`, `TTERRNO`; runs against mounted filesystem fixtures; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx05.c -->
