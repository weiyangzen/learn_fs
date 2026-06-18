<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/openat/openat01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/openat/openat01.c

Purpose: This test case will verify basic function of :manpage:`openat(2)`. - pathname is relative, then it is interpreted relative to the directory referred to by the file descriptor dirfd - pathname is absolute, then dirfd is ignored - ENODIR pathname is a relative pathname and dirfd is a file descriptor referring to a file other than a directory - EBADF dirfd is not a valid file descriptor - pathname is relative and dirfd is the special value AT_FDCWD, then pathname is interpreted relative to the current working directory of the calling process

Important APIs/types/functions: includes `sys/types.h`, `sys/stat.h`, `stdlib.h`, `errno.h`, `string.h`, `stdio.h`, `tst_test.h`; exercises `openat`; defines `verify_openat`, `setup`, `cleanup`; uses flags/constants `AT_FDCWD`, `O_CREAT`, `O_DIRECTORY`, `O_RDWR`.

Control flow centers on `verify_openat`, `setup`, `cleanup`. The `struct tst_test` registration wires `.setup`, `.cleanup`, `.test`, `.tcnt`, `.needs_tmpdir` into the LTP runner. Error-path expectations include `EBADF`, `ENODIR`, `ENOTDIR`.

State and persistence behavior: Runtime state is filesystem fixtures, directory file descriptors, process cwd handling, file status flags, symlinks, atime/mtime metadata, anonymous temporary files, and child exec inheritance of file descriptors.

Dependencies and integration points: Depends on the LTP safe-file helpers, `openat()` or raw syscall fallback, mount/testcase make rules, helper child binaries, and filesystem support for the specific open flags. Direct include dependencies include `sys/types.h`, `sys/stat.h`, `stdlib.h`, `errno.h`, `string.h`, `stdio.h`.

Risks and test signals: Open-flag coverage is filesystem and mount-option sensitive, especially `O_TMPFILE`, `O_NOATIME`, `O_DIRECT`, and large-file offsets. Test signals: reports through `TST_EXP_FAIL2`, `TST_EXP_FD`, `TST_RET`; checks errno values `EBADF`, `ENODIR`, `ENOTDIR`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/openat/openat01.c -->
