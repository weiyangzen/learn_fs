<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx09.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx09.c

Purpose: This code tests if STATX_ATTR_VERITY flag in the statx attributes is set correctly. The statx() system call sets STATX_ATTR_VERITY if the file has fs-verity enabled. This can perform better than FS_IOC_GETFLAGS and FS_IOC_MEASURE_VERITY because it doesn't require opening the file, and opening verity files can be expensive. Minimum Linux version required is v5.5.

Important APIs/types/functions: includes `sys/mount.h`, `stdlib.h`, `stdio.h`, `tst_test.h`, `lapi/fs.h`, `lapi/fsverity.h`, `lapi/stat.h`, `lapi/fcntl.h`; exercises `statx`, `ioctl`, `mount`; defines `test_flagged`, `test_unflagged`, `run`, `flag_setup`, `setup`, `cleanup`; uses constants `AT_FDCWD`, `EINVAL`, `ENOTTY`, `EOPNOTSUPP`, `FS_IOC_ENABLE_VERITY`, `FS_IOC_GETFLAGS`, `FS_IOC_MEASURE_VERITY`, `FS_VERITY_FL`, `FS_VERITY_HASH_ALG_SHA256`, `O_RDONLY`, `STATX_ATTR_VERITY`.

Control flow centers on `test_flagged`, `test_unflagged`, `run`, `flag_setup`, `setup`, `cleanup`. The `struct tst_test` registration wires `.test`, `.tcnt`, `.setup`, `.cleanup`, `.needs_root`, `.needs_device`, `.mntpoint`, `.filesystems`, `.needs_kconfigs`, `.needs_cmds` into the runner. Named case hints include `-O verity`, `CONFIG_FS_VERITY`. Error-path expectations include `EINVAL`, `ENOTTY`, `EOPNOTSUPP`.

State and persistence behavior: Runtime state is filesystem metadata reported through `struct statx`: inode identity, size, timestamps, direct-I/O alignment, mount-root status, and attribute bits set by ioctls, fs-verity, encryption tooling, NFS cache state, or mounted filesystem support.

Dependencies and integration points: Depends on LTP safe file helpers, `lapi/stat.h`, `lapi/fcntl.h`, filesystem ioctl wrappers, mounted test devices, root privileges for attribute/mount cases, and feature probes for fs-verity, encryption, NFS, and DIO alignment. Direct include dependencies include `sys/mount.h`, `stdlib.h`, `stdio.h`, `tst_test.h`, `lapi/fs.h`, `lapi/fsverity.h`.

Risks and test signals: These tests are highly filesystem- and kernel-version-sensitive; unsupported attributes must be skipped or detected, and cleanup must restore inode flags and mounts. Test signals: reports through `TBROK`, `TCONF`, `TERRNO`, `TFAIL`, `TPASS`, `TST_ERR`, `TST_EXP_PASS`, `TST_RET`; checks errno values `EINVAL`, `ENOTTY`, `EOPNOTSUPP`; runs against mounted filesystem fixtures; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx09.c -->
