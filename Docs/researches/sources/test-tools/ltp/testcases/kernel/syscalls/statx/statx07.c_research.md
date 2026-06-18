<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx07.c

Purpose: This code tests the following flags: - AT_STATX_FORCE_SYNC - AT_STATX_DONT_SYNC By exportfs cmd creating NFS setup. A test file is created in server folder and statx is being done in client folder. BY AT_STATX_SYNC_AS_STAT getting predefined mode value. Then, by using AT_STATX_FORCE_SYNC getting new updated vaue from server file changes. BY AT_STATX_SYNC_AS_STAT getting predefined mode value. AT_STATX_FORCE_SYNC is called to create cache data of the file. Then, by using DONT_SYNC_FILE getting old cached data in client folder, but mode has been chaged in server file. The support for SYNC flags was implemented in NFS in: 9ccee940bd5b ("Support statx() mask and query flags parameters")

Important APIs/types/functions: includes `netdb.h`, `stdio.h`, `stdlib.h`, `errno.h`, `linux/limits.h`, `sys/mount.h`, `tst_test.h`, `lapi/stat.h`; exercises `statx`, `sync`, `umask`, `mount`; defines `get_mode`, `test_statx`, `setup`, `cleanup`; uses constants `AT_FDCWD`, `AT_STATX_DONT_SYNC`, `AT_STATX_FORCE_SYNC`, `AT_STATX_SYNC_AS_STAT`, `ECONNREFUSED`, `EOPNOTSUPP`, `ETIMEDOUT`, `STATX_BASIC_STATS`.

Control flow centers on `get_mode`, `test_statx`, `setup`, `cleanup`. The `struct tst_test` registration wires `.tcnt`, `.test`, `.setup`, `.cleanup`, `.needs_tmpdir`, `.filesystems`, `.needs_root`, `.needs_cmds` into the runner. Error-path expectations include `ECONNREFUSED`, `EOPNOTSUPP`, `ETIMEDOUT`.

State and persistence behavior: Runtime state is filesystem metadata reported through `struct statx`: inode identity, size, timestamps, direct-I/O alignment, mount-root status, and attribute bits set by ioctls, fs-verity, encryption tooling, NFS cache state, or mounted filesystem support.

Dependencies and integration points: Depends on LTP safe file helpers, `lapi/stat.h`, `lapi/fcntl.h`, filesystem ioctl wrappers, mounted test devices, root privileges for attribute/mount cases, and feature probes for fs-verity, encryption, NFS, and DIO alignment. Direct include dependencies include `netdb.h`, `stdio.h`, `stdlib.h`, `errno.h`, `linux/limits.h`, `sys/mount.h`.

Risks and test signals: These tests are highly filesystem- and kernel-version-sensitive; unsupported attributes must be skipped or detected, and cleanup must restore inode flags and mounts. Test signals: reports through `TBROK`, `TCONF`, `TERRNO`, `TFAIL`, `TINFO`, `TPASS`, `TST_ERR`, `TST_RET`; checks errno values `ECONNREFUSED`, `EOPNOTSUPP`, `ETIMEDOUT`; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/statx/statx07.c -->
