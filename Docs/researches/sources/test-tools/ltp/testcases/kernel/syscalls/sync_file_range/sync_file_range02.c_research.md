<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sync_file_range/sync_file_range02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sync_file_range/sync_file_range02.c

Purpose: Tests if sync_file_range() does sync a test file range with a many dirty pages to a block device. Also, it tests all supported filesystems on a test block device. Fat does not support sparse files, we have to pre-fill the file so that the zero-filled start of the file has been written to disk before the test starts.

Important APIs/types/functions: includes `errno.h`, `stdlib.h`, `stdio.h`, `sys/types.h`, `tst_test.h`, `lapi/sync_file_range.h`, `check_sync_file_range.h`; exercises `sync`, `sync_file_range`, `write`; defines `verify_sync_file_range`, `run`, `setup`; uses constants `O_CREAT`, `O_RDONLY`, `O_RDWR`.

Control flow centers on `verify_sync_file_range`, `run`, `setup`. The `struct tst_test` registration wires `.tcnt`, `.needs_root`, `.mount_device`, `.all_filesystems`, `.skip_filesystems`, `.mntpoint`, `.setup`, `.test` into the runner. Named case hints include `fuse`.

State and persistence behavior: Runtime state is dirty file ranges, file descriptors, offsets, flags, and block-device write counters before and after `sync_file_range()`.

Dependencies and integration points: Depends on `check_sync_file_range.h`, raw syscall wrappers, mounted test devices for writeback observation, and ordinary temp files for error paths. Direct include dependencies include `errno.h`, `stdlib.h`, `stdio.h`, `sys/types.h`, `tst_test.h`, `lapi/sync_file_range.h`.

Risks and test signals: Range writeback behavior varies by filesystem and kernel; invalid-argument tests must distinguish unsupported syscall from real failure. Test signals: reports through `TCONF`, `TFAIL`, `TINFO`, `TPASS`, `TST_MB`, `TST_RET`, `TTERRNO`; runs against mounted filesystem fixtures; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sync_file_range/sync_file_range02.c -->
