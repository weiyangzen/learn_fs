<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/syncfs/syncfs01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/syncfs/syncfs01.c

Purpose: Test syncfs It basically tests syncfs() to sync filesystem having large dirty file pages to block device. Also, it tests all supported filesystems on a test block device.

Important APIs/types/functions: includes `stdlib.h`, `stdio.h`, `sys/types.h`, `tst_test.h`, `lapi/syncfs.h`, `check_syncfs.h`; exercises `sync`, `syncfs`; defines `verify_syncfs`, `setup`; uses constants `O_CREAT`, `O_RDWR`.

Control flow centers on `verify_syncfs`, `setup`. The `struct tst_test` registration wires `.needs_root`, `.mount_device`, `.all_filesystems`, `.skip_filesystems`, `.mntpoint`, `.setup`, `.test_all` into the runner. Named case hints include `tmpfs`.

State and persistence behavior: Runtime state is dirty data tied to a specific mounted filesystem and file descriptor; only that filesystem should be flushed by `syncfs()`.

Dependencies and integration points: Depends on `check_syncfs.h`, raw syscall wrappers, mounted test devices, block write counters, and per-filesystem descriptor setup. Direct include dependencies include `stdlib.h`, `stdio.h`, `sys/types.h`, `tst_test.h`, `lapi/syncfs.h`, `check_syncfs.h`.

Risks and test signals: Per-filesystem flush accounting is timing-sensitive and depends on block-device counter accuracy. Test signals: reports through `TFAIL`, `TPASS`, `TST_MB`, `TST_RET`, `TTERRNO`; runs against mounted filesystem fixtures; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/syncfs/syncfs01.c -->
