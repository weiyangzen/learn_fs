<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sync/sync01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sync/sync01.c

Purpose: sync03 It basically tests sync() to sync test file having large dirty file pages to block device. Also, it tests all supported filesystems on a test block device.

Important APIs/types/functions: includes `errno.h`, `stdlib.h`, `stdio.h`, `sys/types.h`, `tst_test.h`; exercises `sync`; defines `verify_sync`; uses constants `O_CREAT`, `O_RDWR`.

Control flow centers on `verify_sync`. The `struct tst_test` registration wires `.needs_root`, `.mount_device`, `.all_filesystems`, `.skip_filesystems`, `.mntpoint`, `.test_all` into the runner. Named case hints include `tmpfs`.

State and persistence behavior: Runtime state is dirty page cache and block-device write counters around `sync()`/`tst_dev_sync()` on a mounted test filesystem.

Dependencies and integration points: Depends on a mounted block device, dirtying helpers such as `tst_fill_fd()`, device write counters, and filesystem skip lists. Direct include dependencies include `errno.h`, `stdlib.h`, `stdio.h`, `sys/types.h`, `tst_test.h`.

Risks and test signals: Writeback counters are timing- and filesystem-sensitive; delayed or background writeback can create noisy signals. Test signals: reports through `TFAIL`, `TPASS`, `TST_MB`; runs against mounted filesystem fixtures; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sync/sync01.c -->
