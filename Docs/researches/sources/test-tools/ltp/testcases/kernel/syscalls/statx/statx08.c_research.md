<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx08.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx08.c

Purpose: This case tests whether the attributes field of statx received expected value by using flags in the stx_attributes_mask field of statx. File set with following flags by using SAFE_IOCTL: - STATX_ATTR_COMPRESSED: The file is compressed by the filesystem. - STATX_ATTR_IMMUTABLE: The file cannot be modified. - STATX_ATTR_APPEND: The file can only be opened in append mode for writing. - STATX_ATTR_NODUMP: File is not a candidate for backup when a backup program such as dump(8) is run. Two directories are tested. First directory has all flags set. Second directory has no flags set. ntfs3g fuse fs returns wrong errno for unimplemented ioctls

Important APIs/types/functions: includes `tst_test.h`, `lapi/fs.h`, `stdlib.h`, `lapi/stat.h`, `lapi/fcntl.h`; exercises `statx`, `ioctl`; defines `run`, `caid_flags_setup`, `setup`, `cleanup`; uses constants `AT_FDCWD`, `ENOTTY`, `FS_APPEND_FL`, `FS_COMPR_FL`, `FS_IMMUTABLE_FL`, `FS_IOC_GETFLAGS`, `FS_IOC_SETFLAGS`, `FS_NODUMP_FL`, `O_DIRECTORY`, `O_RDONLY`, `STATX_ATTR_APPEND`, `STATX_ATTR_COMPRESSED`, `STATX_ATTR_IMMUTABLE`, `STATX_ATTR_NODUMP`.

Control flow centers on `run`, `caid_flags_setup`, `setup`, `cleanup`. The `struct tst_test` registration wires `.test`, `.tcnt`, `.setup`, `.cleanup`, `.needs_root`, `.all_filesystems`, `.mount_device`, `.mntpoint` into the runner. Error-path expectations include `ENOTTY`.

State and persistence behavior: Runtime state is filesystem metadata reported through `struct statx`: inode identity, size, timestamps, direct-I/O alignment, mount-root status, and attribute bits set by ioctls, fs-verity, encryption tooling, NFS cache state, or mounted filesystem support.

Dependencies and integration points: Depends on LTP safe file helpers, `lapi/stat.h`, `lapi/fcntl.h`, filesystem ioctl wrappers, mounted test devices, root privileges for attribute/mount cases, and feature probes for fs-verity, encryption, NFS, and DIO alignment. Direct include dependencies include `tst_test.h`, `lapi/fs.h`, `stdlib.h`, `lapi/stat.h`, `lapi/fcntl.h`.

Risks and test signals: These tests are highly filesystem- and kernel-version-sensitive; unsupported attributes must be skipped or detected, and cleanup must restore inode flags and mounts. Test signals: reports through `TBROK`, `TCONF`, `TERRNO`, `TFAIL`, `TPASS`, `TST_RET`, `TTERRNO`; checks errno values `ENOTTY`; runs against mounted filesystem fixtures; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx08.c -->
