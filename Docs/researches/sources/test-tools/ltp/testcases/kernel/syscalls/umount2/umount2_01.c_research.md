<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/umount2/umount2_01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/umount2/umount2_01.c

Purpose: This program is distributed in the hope that it would be useful, but alone with this program. DESCRIPTION Test for feature MNT_DETACH of umount2(). "Perform a lazy unmount: make the mount point unavailable for new accesses, and actually perform the unmount when the mount point ceases to be busy." check the unavailability for new access check the old fd still points to the file in previous mount point and is available

Important APIs/types/functions: includes `errno.h`, `test.h`, `tso_safe_macros.h`, `lapi/mount.h`; exercises `umount`, `umount2`, `mount`, `close`; defines `setup`, `umount2_verify`, `cleanup`, `main`; uses constants `EXIT`, `MNT_DETACH`, `O_RDONLY`.

Control flow centers on `setup`, `umount2_verify`, `cleanup`, `main`. This is an older harness test using `tst_parse_opts()`, `TEST_LOOPING()`, and explicit cleanup. Error-path expectations include `EXIT`.

State and persistence behavior: Runtime state is mounted filesystems plus `umount2()` flags such as forced, lazy, expire, and no-follow behavior.

Dependencies and integration points: Depends on raw `umount2()` or libc wrapper, mount helpers, device acquisition in legacy tests, and flag-specific kernel semantics. Direct include dependencies include `errno.h`, `test.h`, `tso_safe_macros.h`, `lapi/mount.h`.

Risks and test signals: Flag combinations have special kernel behavior and legacy device handling can leave mounted filesystems if cleanup is incomplete. Test signals: reports through `TBROK`, `TCONF`, `TERRNO`, `TFAIL`, `TPASS`, `TST_TOTAL`, `TTERRNO`; checks errno values `EXIT`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/umount2/umount2_01.c -->
