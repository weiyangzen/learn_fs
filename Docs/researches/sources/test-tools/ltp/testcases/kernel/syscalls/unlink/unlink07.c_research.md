<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unlink/unlink07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/unlink/unlink07.c

Purpose: Verify that :manpage:`unlink(2)`: fails with: - ENOENT when file does not exist - ENOENT when pathname is empty - ENOENT when a component in pathname does not exist - EFAULT when pathname points outside the accessible address space - ENOTDIR when a component used as a directory in pathname is not, in fact, a directory - ENAMETOOLONG when pathname is too long

Important APIs/types/functions: includes `errno.h`, `limits.h`, `string.h`, `unistd.h`, `tst_test.h`; exercises `unlink`; defines `verify_unlink`, `setup`; uses constants `EFAULT`, `ENAMETOOLONG`, `ENOENT`, `ENOTDIR`.

Control flow centers on `verify_unlink`, `setup`. The `struct tst_test` registration wires `.needs_tmpdir`, `.setup`, `.tcnt`, `.test` into the runner. Named case hints include `nonexistfile`, `nefile/file`, `file/file`. Error-path expectations include `EFAULT`, `ENAMETOOLONG`, `ENOENT`, `ENOTDIR`.

State and persistence behavior: Runtime state is directory entries, inode flags, filesystem writability, process credentials, permissions, and temporary path fixtures.

Dependencies and integration points: Depends on temporary path fixtures, root/non-root credentials, filesystem inode flags, mounted read-only filesystems, and safe cleanup. Direct include dependencies include `errno.h`, `limits.h`, `string.h`, `unistd.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TST_EXP_FAIL`; checks errno values `EFAULT`, `ENAMETOOLONG`, `ENOENT`, `ENOTDIR`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unlink/unlink07.c -->
