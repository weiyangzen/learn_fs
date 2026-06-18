<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/umask/umask01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/umask/umask01.c

Purpose: 07/2001 Ported by John George umask(2) sets the mask from 0000 to 0777 while we create files, the previous value of the mask should be returned correctly, and the file mode should be correct for each creation mask.

Important APIs/types/functions: includes `errno.h`, `stdio.h`, `sys/types.h`, `sys/stat.h`, `tst_test.h`; exercises `umask`; defines `verify_umask`.

Control flow centers on `verify_umask`. The `struct tst_test` registration wires `.test_all`, `.needs_tmpdir` into the runner.

State and persistence behavior: Runtime state is the process file creation mask and resulting modes of newly created files.

Dependencies and integration points: Depends on process umask state, file creation helpers, and stat-visible permission bits. Direct include dependencies include `errno.h`, `stdio.h`, `sys/types.h`, `sys/stat.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_RET`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/umask/umask01.c -->
