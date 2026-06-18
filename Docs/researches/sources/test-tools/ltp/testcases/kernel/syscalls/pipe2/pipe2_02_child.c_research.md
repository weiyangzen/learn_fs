<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe2/pipe2_02_child.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pipe2/pipe2_02_child.c

Purpose: Companion exec helper for the pipe2 close-on-exec test; it attempts descriptor use after exec to distinguish inherited fds from `O_CLOEXEC` fds.

Important APIs/types/functions: includes `stdio.h`, `stdlib.h`, `string.h`, `errno.h`, `fcntl.h`; exercises `fcntl`; defines `main`.

Control flow centers on `main`. Error-path expectations include `EBADF`.

State and persistence behavior: Runtime state is pipe file descriptors returned atomically with requested flags such as `O_CLOEXEC`, `O_NONBLOCK`, and packet/notification modes where available.

Dependencies and integration points: Depends on pipe2 syscall wrappers, helper child binaries for close-on-exec checks, fcntl status flags, and kernel support for newer pipe flags. Direct include dependencies include `stdio.h`, `stdlib.h`, `string.h`, `errno.h`, `fcntl.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: checks errno values `EBADF`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe2/pipe2_02_child.c -->
