<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx12.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx12.c

Purpose: It is a basic test for STATX_ATTR_MOUNT_ROOT flag. This flag indicates whether the path or fd refers to the root of a mount or not. Minimum Linux version required is v5.8.

Important APIs/types/functions: includes `unistd.h`, `stdlib.h`, `stdbool.h`, `stdio.h`, `tst_test.h`, `lapi/stat.h`; exercises `statx`, `mount`; defines `verify_statx`, `setup`, `cleanup`; uses constants `AT_EMPTY_PATH`, `AT_FDCWD`, `O_DIRECTORY`, `O_RDWR`, `STATX_ATTR_MOUNT_ROOT`.

Control flow centers on `verify_statx`, `setup`, `cleanup`. The `struct tst_test` registration wires `.test`, `.setup`, `.cleanup`, `.mntpoint`, `.mount_device`, `.all_filesystems`, `.needs_root`, `.tcnt` into the runner.

State and persistence behavior: Runtime state is filesystem metadata reported through `struct statx`: inode identity, size, timestamps, direct-I/O alignment, mount-root status, and attribute bits set by ioctls, fs-verity, encryption tooling, NFS cache state, or mounted filesystem support.

Dependencies and integration points: Depends on LTP safe file helpers, `lapi/stat.h`, `lapi/fcntl.h`, filesystem ioctl wrappers, mounted test devices, root privileges for attribute/mount cases, and feature probes for fs-verity, encryption, NFS, and DIO alignment. Direct include dependencies include `unistd.h`, `stdlib.h`, `stdbool.h`, `stdio.h`, `tst_test.h`, `lapi/stat.h`.

Risks and test signals: These tests are highly filesystem- and kernel-version-sensitive; unsupported attributes must be skipped or detected, and cleanup must restore inode flags and mounts. Test signals: reports through `TCONF`, `TFAIL`, `TINFO`, `TPASS`, `TST_EXP_PASS_SILENT`; runs against mounted filesystem fixtures; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx12.c -->
