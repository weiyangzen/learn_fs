<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/umount/umount03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/umount/umount03.c

Purpose: Verify that :manpage:`umount(2)` returns -1 and sets errno to EPERM if the user is not the super-user.

Important APIs/types/functions: includes `pwd.h`, `sys/mount.h`, `tst_test.h`; exercises `umount`, `mount`; defines `verify_umount`, `setup`, `cleanup`; uses constants `EPERM`.

Control flow centers on `verify_umount`, `setup`, `cleanup`. The `struct tst_test` registration wires `.needs_root`, `.setup`, `.cleanup`, `.test_all` into the runner. Error-path expectations include `EPERM`.

State and persistence behavior: Runtime state is mounted test filesystems, busy file descriptors, path validity, privileges, and cleanup unmount attempts.

Dependencies and integration points: Depends on root privileges, mount helpers, temporary mountpoints, busy file descriptors, and path/error fixtures. Direct include dependencies include `pwd.h`, `sys/mount.h`, `tst_test.h`.

Risks and test signals: Unmount tests can leave mounted fixtures on failure; busy-mount cases must close descriptors before cleanup. Test signals: reports through `TERRNO`, `TST_EXP_FAIL`; checks errno values `EPERM`; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/umount/umount03.c -->
