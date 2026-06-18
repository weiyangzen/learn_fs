<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx04.c

Purpose: Test whether the kernel properly advertises support for statx() attributes: - STATX_ATTR_COMPRESSED: The file is compressed by the filesystem. - STATX_ATTR_IMMUTABLE: The file cannot be modified. - STATX_ATTR_APPEND: The file can only be opened in append mode for writing. - STATX_ATTR_NODUMP: File is not a candidate for backup when a backup program such as dump(8) is run. xfs filesystem doesn't support STATX_ATTR_COMPRESSED flag, so we only test three other flags. ext2, ext4, btrfs, xfs and tmpfs support statx syscall since the following commit commit 93bc420ed41df63a18ae794101f7cbf45226a6ef Date: Mon Feb 18 09:07:02 2019 +0800 ext2: support statx syscall commit 99652ea56a4186bc5bf8a3721c5353f41b35ebcb Date: Fri Mar 31 18:31:56 2017 +0100 ext4: Add statx support commit 04a87e3472828f769a93655d7c64a27573bdbc2c Date: Fri May 12 15:07:43 201

Important APIs/types/functions: includes `stdlib.h`, `tst_test.h`, `lapi/fs.h`, `lapi/stat.h`, `lapi/fcntl.h`; exercises `statx`, `syscall`, `ioctl`; defines `setup`, `run`; uses constants `AT_FDCWD`, `ENOTTY`, `FS_IOC_`, `FS_IOC_GETFLAGS`, `O_DIRECTORY`, `O_RDONLY`, `STATX_ATTR_APPEND`, `STATX_ATTR_COMPRESSED`, `STATX_ATTR_IMMUTABLE`, `STATX_ATTR_NODUMP`.

Control flow centers on `setup`, `run`. The `struct tst_test` registration wires `.test_all`, `.setup`, `.needs_root`, `.all_filesystems`, `.mount_device`, `.mntpoint`, `.skip_filesystems`, `.tags` into the runner. Named case hints include `fuse`, `linux-git`. Error-path expectations include `ENOTTY`.

State and persistence behavior: Runtime state is filesystem metadata reported through `struct statx`: inode identity, size, timestamps, direct-I/O alignment, mount-root status, and attribute bits set by ioctls, fs-verity, encryption tooling, NFS cache state, or mounted filesystem support.

Dependencies and integration points: Depends on LTP safe file helpers, `lapi/stat.h`, `lapi/fcntl.h`, filesystem ioctl wrappers, mounted test devices, root privileges for attribute/mount cases, and feature probes for fs-verity, encryption, NFS, and DIO alignment. Direct include dependencies include `stdlib.h`, `tst_test.h`, `lapi/fs.h`, `lapi/stat.h`, `lapi/fcntl.h`.

Risks and test signals: These tests are highly filesystem- and kernel-version-sensitive; unsupported attributes must be skipped or detected, and cleanup must restore inode flags and mounts. Test signals: reports through `TBROK`, `TCONF`, `TFAIL`, `TPASS`, `TST_ERR`, `TST_EXP_PASS_SILENT`, `TST_RET`, `TTERRNO`; checks errno values `ENOTTY`; runs against mounted filesystem fixtures; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx04.c -->
