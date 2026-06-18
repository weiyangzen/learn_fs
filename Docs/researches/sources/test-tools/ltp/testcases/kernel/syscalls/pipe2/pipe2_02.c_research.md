<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe2/pipe2_02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pipe2/pipe2_02.c

Purpose: This case is designed to test the basic functionality about the O_CLOEXEC flag of pipe2.

Important APIs/types/functions: includes `stdio.h`, `unistd.h`, `stdlib.h`, `lapi/fcntl.h`, `tst_test.h`; exercises `pipe2`, `execlp`, `fcntl`; defines `cleanup`, `verify_pipe2`; uses flags/constants `O_CLOEXEC`.

Control flow centers on `cleanup`, `verify_pipe2`. The `struct tst_test` registration wires `.cleanup`, `.forks_child`, `.needs_root`, `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is pipe file descriptors returned atomically with requested flags such as `O_CLOEXEC`, `O_NONBLOCK`, and packet/notification modes where available.

Dependencies and integration points: Depends on pipe2 syscall wrappers, helper child binaries for close-on-exec checks, fcntl status flags, and kernel support for newer pipe flags. Direct include dependencies include `stdio.h`, `unistd.h`, `stdlib.h`, `lapi/fcntl.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TBROK`, `TFAIL`, `TPASS`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe2/pipe2_02.c -->
