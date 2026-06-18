<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx06.c

Purpose: Test the following file timestamps of statx syscall: - btime - The time before and after the execution of the create system call is noted. - mtime - The time before and after the execution of the write system call is noted. - atime - The time before and after the execution of the read system call is noted. - ctime - The time before and after the execution of the chmod system call is noted.

Important APIs/types/functions: includes `stdio.h`, `time.h`, `tst_test.h`, `tst_safe_clocks.h`, `tst_safe_macros.h`, `tst_timer.h`, `lapi/stat.h`, `lapi/mount.h`; exercises `statx`, `syscall`, `time`, `mount`, `read`, `write`, `chmod`; defines `timestamp_to_timespec`, `clock_wait_tick`, `create_file`, `write_file`, `read_file`, `change_mode`, `test_statx`, `cleanup`; uses constants `AT_FDCWD`, `CLOCK_REALTIME`, `CLOCK_REALTIME_COARSE`, `O_CREAT`, `O_RDWR`, `STATX_BASIC_STATS`, `STATX_BTIME`.

Control flow centers on `timestamp_to_timespec`, `clock_wait_tick`, `create_file`, `write_file`, `read_file`, `change_mode`, `test_statx`, `cleanup`. The `struct tst_test` registration wires `.cleanup`, `.tcnt`, `.test`, `.needs_root`, `.mntpoint`, `.mount_device`, `.filesystems` into the runner. Named case hints include `-I`.

State and persistence behavior: Runtime state is filesystem metadata reported through `struct statx`: inode identity, size, timestamps, direct-I/O alignment, mount-root status, and attribute bits set by ioctls, fs-verity, encryption tooling, NFS cache state, or mounted filesystem support.

Dependencies and integration points: Depends on LTP safe file helpers, `lapi/stat.h`, `lapi/fcntl.h`, filesystem ioctl wrappers, mounted test devices, root privileges for attribute/mount cases, and feature probes for fs-verity, encryption, NFS, and DIO alignment. Direct include dependencies include `stdio.h`, `time.h`, `tst_test.h`, `tst_safe_clocks.h`, `tst_safe_macros.h`, `tst_timer.h`.

Risks and test signals: These tests are highly filesystem- and kernel-version-sensitive; unsupported attributes must be skipped or detected, and cleanup must restore inode flags and mounts. Test signals: reports through `TFAIL`, `TPASS`, `TST_RET`, `TTERRNO`; runs against mounted filesystem fixtures; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx06.c -->
