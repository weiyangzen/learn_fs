<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/umount2/umount2_02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/umount2/umount2_02.c

Purpose: Test for feature MNT_EXPIRE of :manpage:`umount2(2)`: - EINVAL when flag is specified with either MNT_FORCE or MNT_DETACH - EAGAIN when initial call to :manpage:`umount2(2)` with MNT_EXPIRE - EAGAIN when :manpage:`umount2(2)` with MNT_EXPIRE after :manpage:`access(2)` - succeed when second call to :manpage:`umount2(2)` with MNT_EXPIRE Test for feature UMOUNT_NOFOLLOW of :manpage:`umount2(2)`: - EINVAL when target is a symbolic link - succeed when target is a mount point

Important APIs/types/functions: includes `lapi/mount.h`, `tst_test.h`; exercises `symlink`, `umount`, `umount2`, `mount`; defines `umount2_retry`, `test_umount2`, `setup`, `cleanup`; uses constants `EAGAIN`, `EBUSY`, `EINVAL`, `MNT_DETACH`, `MNT_EXPIRE`, `MNT_FORCE`, `UMOUNT_NOFOLLOW`.

Control flow centers on `umount2_retry`, `test_umount2`, `setup`, `cleanup`. The `struct tst_test` registration wires `.tcnt`, `.cleanup`, `.setup`, `.needs_root`, `.mntpoint`, `.test` into the runner. Named case hints include `umount2(`. Error-path expectations include `EAGAIN`, `EBUSY`, `EINVAL`.

State and persistence behavior: Runtime state is mounted filesystems plus `umount2()` flags such as forced, lazy, expire, and no-follow behavior.

Dependencies and integration points: Depends on raw `umount2()` or libc wrapper, mount helpers, device acquisition in legacy tests, and flag-specific kernel semantics. Direct include dependencies include `lapi/mount.h`, `tst_test.h`.

Risks and test signals: Flag combinations have special kernel behavior and legacy device handling can leave mounted filesystems if cleanup is incomplete. Test signals: reports through `TINFO`, `TST_EXP_FAIL`, `TST_EXP_PASS`, `TST_PASS`; checks errno values `EAGAIN`, `EBUSY`, `EINVAL`; runs against mounted filesystem fixtures; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/umount2/umount2_02.c -->
