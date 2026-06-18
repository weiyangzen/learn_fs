<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getcwd/getcwd02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getcwd/getcwd02.c

Purpose:  Testcase to check the basic functionality of the getcwd(2) system call. 1. getcwd(2) works fine if buf and size are valid. 2. getcwd(2) works fine if buf points to NULL and size is set to 0. 3. getcwd(2) works fine if buf points to NULL and size is greater than strlen(path).

Important APIs/types/functions: includes `errno.h`, `unistd.h`, `stdlib.h`, `string.h`, `sys/types.h`, `sys/stat.h`, `tst_test.h`; touches `getcwd`; defines `dir_exists`, `verify_getcwd`, `setup`; uses LTP safe helpers such as `SAFE_CHDIR`.

Control flow centers on `dir_exists`, `verify_getcwd`, `setup`. The `struct tst_test` registration wires `.setup`, `.tcnt`, `.test` into the LTP runner.

State and persistence behavior: Runtime state is the process current working directory and path dentries; several tests mutate directories, symlinks, or renamed paths while checking returned buffers and errors.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `errno.h`, `unistd.h`, `stdlib.h`, `string.h`, `sys/types.h`, `sys/stat.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TBROK`, `TFAIL`, `TPASS`, `TST_ERR`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getcwd/getcwd02.c -->
