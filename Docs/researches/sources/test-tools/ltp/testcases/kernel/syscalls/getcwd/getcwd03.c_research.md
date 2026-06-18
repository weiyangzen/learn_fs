<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getcwd/getcwd03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getcwd/getcwd03.c

Purpose:  Testcase to check the basic functionality of the getcwd(2) system call on a symbolic link. [Algorithm] 1. create a directory, and create a symbolic link to it at the same directory level. 2. get the working directory of a directory, and its pathname. 3. get the working directory of a symbolic link, and its pathname, and its readlink info. 4. compare the working directories and link information.

Important APIs/types/functions: includes `errno.h`, `stdio.h`, `string.h`, `stdlib.h`, `sys/stat.h`, `sys/types.h`, `stdlib.h`, `tst_test.h`; touches `getcwd`, `getpid`; defines `verify_getcwd`, `setup`; uses LTP safe helpers such as `SAFE_BASENAME`, `SAFE_CHDIR`, `SAFE_MKDIR`, `SAFE_READLINK`, `SAFE_SYMLINK`.

Control flow centers on `verify_getcwd`, `setup`. The `struct tst_test` registration wires `.needs_tmpdir`, `.setup`, `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is the process current working directory and path dentries; several tests mutate directories, symlinks, or renamed paths while checking returned buffers and errors.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `errno.h`, `stdio.h`, `string.h`, `stdlib.h`, `sys/stat.h`, `sys/types.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TFAIL`, `TPASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getcwd/getcwd03.c -->
