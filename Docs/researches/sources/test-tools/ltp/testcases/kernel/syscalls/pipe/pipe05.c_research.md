<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe05.c

Purpose: Legacy negative pipe test that passes an invalid userspace descriptor array pointer and expects `pipe()` to fail with `EFAULT`.

Important APIs/types/functions: includes `fcntl.h`, `errno.h`, `setjmp.h`, `test.h`; exercises `pipe`, `write`, `fcntl`; defines `setup`, `cleanup`, `sig11_handler`, `main`.

Control flow centers on `setup`, `cleanup`, `sig11_handler`, `main`. Error-path expectations include `EFAULT`, `EMFILE`.

State and persistence behavior: Runtime state is anonymous pipe file descriptors, pipe buffer contents/capacity, blocking and nonblocking status flags, EOF behavior, and descriptor inheritance.

Dependencies and integration points: Depends on LTP pipe/fcntl/safe I/O helpers, temporary processes, optional resource-limit changes, and blocking/nonblocking pipe semantics. Direct include dependencies include `fcntl.h`, `errno.h`, `setjmp.h`, `test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_TOTAL`; checks errno values `EFAULT`, `EMFILE`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe05.c -->
