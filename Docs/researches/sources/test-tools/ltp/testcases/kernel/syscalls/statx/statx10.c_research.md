<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx10.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx10.c

Purpose: It is a basic test for STATX_DIOALIGN mask on ext4 and xfs filesystem. - STATX_DIOALIGN Want stx_dio_mem_align and stx_dio_offset_align value Check these two values are nonzero under dio situation when STATX_DIOALIGN in the request mask. On ext4, files that use certain filesystem features (data journaling, encryption, and verity) fall back to buffered I/O. But ltp creates own filesystem by enabling mount_device in tst_test struct. If we set block device to LTP_DEV environment, we use this block device to mount by using default mount option. Otherwise, use loop device to simuate it. So it can avoid these above situations and don't fall back to buffered I/O. Minimum Linux version required is v6.1.

Important APIs/types/functions: includes `sys/types.h`, `unistd.h`, `stdlib.h`, `stdbool.h`, `tst_test.h`, `lapi/stat.h`, `lapi/fcntl.h`; exercises `statx`, `mount`, `open`; defines `verify_statx`, `setup`; uses constants `AT_FDCWD`, `EINVAL`, `O_DIRECT`, `O_RDWR`, `STATX_DIOALIGN`.

Control flow centers on `verify_statx`, `setup`. The `struct tst_test` registration wires `.test_all`, `.setup`, `.needs_root`, `.mntpoint`, `.mount_device`, `.all_filesystems` into the runner. Error-path expectations include `EINVAL`.

State and persistence behavior: Runtime state is filesystem metadata reported through `struct statx`: inode identity, size, timestamps, direct-I/O alignment, mount-root status, and attribute bits set by ioctls, fs-verity, encryption tooling, NFS cache state, or mounted filesystem support.

Dependencies and integration points: Depends on LTP safe file helpers, `lapi/stat.h`, `lapi/fcntl.h`, filesystem ioctl wrappers, mounted test devices, root privileges for attribute/mount cases, and feature probes for fs-verity, encryption, NFS, and DIO alignment. Direct include dependencies include `sys/types.h`, `unistd.h`, `stdlib.h`, `stdbool.h`, `tst_test.h`, `lapi/stat.h`.

Risks and test signals: These tests are highly filesystem- and kernel-version-sensitive; unsupported attributes must be skipped or detected, and cleanup must restore inode flags and mounts. Test signals: reports through `TBROK`, `TCONF`, `TERRNO`, `TFAIL`, `TPASS`, `TST_EXP_PASS_SILENT`; checks errno values `EINVAL`; runs against mounted filesystem fixtures; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx10.c -->
