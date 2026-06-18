<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unlinkat/unlinkat01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/unlinkat/unlinkat01.c

Purpose: Basic :manpage:`unlinkat(2)` test. tesfile2 will be unlinked by test0. testfile3 will be unlined by test1.

Important APIs/types/functions: includes `tst_test.h`, `lapi/syscalls.h`, `tst_safe_stdio.h`, `lapi/fcntl.h`; exercises `unlinkat`; defines `getfd`, `run`, `setup`, `cleanup`; uses constants `AT_FDCWD`, `AT_REMOVEDIR`, `EBADF`, `EINVAL`, `ENOTDIR`, `O_CREAT`, `O_DIRECTORY`, `O_RDWR`.

Control flow centers on `getfd`, `run`, `setup`, `cleanup`. The `struct tst_test` registration wires `.needs_tmpdir`, `.tcnt`, `.setup`, `.test`, `.cleanup` into the runner. Error-path expectations include `EBADF`, `EINVAL`, `ENOTDIR`.

State and persistence behavior: Runtime state is directory file descriptors, cwd-relative paths, flags, and directory/file removal fixtures.

Dependencies and integration points: Depends on directory fd setup, path construction, `unlinkat()` flags, and temporary directory cleanup. Direct include dependencies include `tst_test.h`, `lapi/syscalls.h`, `tst_safe_stdio.h`, `lapi/fcntl.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_ERR`, `TTERRNO`; checks errno values `EBADF`, `EINVAL`, `ENOTDIR`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/unlinkat/unlinkat01.c -->
