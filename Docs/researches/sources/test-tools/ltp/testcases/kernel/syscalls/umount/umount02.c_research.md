<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/umount/umount02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/umount/umount02.c

Purpose: Check for basic errors returned by :manpage:`umount(2)` system call. Verify that :manpage:`umount(2)` returns -1 and sets errno to 1. EBUSY if it cannot be umounted, because dir is still busy. 2. EFAULT if specialfile or device file points to invalid address space. 3. ENOENT if pathname was empty or has a nonexistent component. 4. EINVAL if specialfile or device is invalid or not a mount point. 5. ENAMETOOLONG if pathname was longer than MAXPATHLEN.

Important APIs/types/functions: includes `sys/mount.h`, `tst_test.h`; exercises `umount`, `mount`; defines `verify_umount`, `setup`, `cleanup`; uses constants `EBUSY`, `EFAULT`, `EINVAL`, `ENAMETOOLONG`, `ENOENT`.

Control flow centers on `verify_umount`, `setup`, `cleanup`. The `struct tst_test` registration wires `.tcnt`, `.needs_root`, `.setup`, `.cleanup`, `.test` into the runner. Named case hints include `Already mounted/busy`, `Invalid address`, `Directory not found`, `Invalid  device`, `Pathname too long`. Error-path expectations include `EBUSY`, `EFAULT`, `EINVAL`, `ENAMETOOLONG`, `ENOENT`.

State and persistence behavior: Runtime state is mounted test filesystems, busy file descriptors, path validity, privileges, and cleanup unmount attempts.

Dependencies and integration points: Depends on root privileges, mount helpers, temporary mountpoints, busy file descriptors, and path/error fixtures. Direct include dependencies include `sys/mount.h`, `tst_test.h`.

Risks and test signals: Unmount tests can leave mounted fixtures on failure; busy-mount cases must close descriptors before cleanup. Test signals: reports through `TST_EXP_FAIL`; checks errno values `EBUSY`, `EFAULT`, `EINVAL`, `ENAMETOOLONG`, `ENOENT`; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/umount/umount02.c -->
