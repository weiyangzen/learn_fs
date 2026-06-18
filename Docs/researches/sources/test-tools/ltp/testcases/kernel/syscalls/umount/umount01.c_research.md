<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/umount/umount01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/umount/umount01.c

Purpose: Check the basic functionality of the :manpage:`umount(2)` system call.

Important APIs/types/functions: includes `sys/mount.h`, `tst_test.h`; exercises `umount`, `mount`; defines `verify_umount`, `setup`, `cleanup`; uses constants `EBUSY`.

Control flow centers on `verify_umount`, `setup`, `cleanup`. The `struct tst_test` registration wires `.needs_root`, `.setup`, `.cleanup`, `.test_all` into the runner. Error-path expectations include `EBUSY`.

State and persistence behavior: Runtime state is mounted test filesystems, busy file descriptors, path validity, privileges, and cleanup unmount attempts.

Dependencies and integration points: Depends on root privileges, mount helpers, temporary mountpoints, busy file descriptors, and path/error fixtures. Direct include dependencies include `sys/mount.h`, `tst_test.h`.

Risks and test signals: Unmount tests can leave mounted fixtures on failure; busy-mount cases must close descriptors before cleanup. Test signals: reports through `TINFO`, `TST_ERR`, `TST_EXP_PASS`, `TST_RET`; checks errno values `EBUSY`; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/umount/umount01.c -->
