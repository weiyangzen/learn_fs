<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe09.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe09.c

Purpose: Legacy functional pipe test checking that two writer children can use the same pipe and the parent receives data from both writers.

Important APIs/types/functions: includes `unistd.h`, `signal.h`, `sys/wait.h`, `errno.h`, `test.h`, `tso_safe_macros.h`; exercises `pipe`, `fork`, `read`, `write`; defines `setup`, `cleanup`, `do_read`, `main`.

Control flow centers on `setup`, `cleanup`, `do_read`, `main`. Error-path expectations include `EINTR`.

State and persistence behavior: Runtime state is anonymous pipe file descriptors, pipe buffer contents/capacity, blocking and nonblocking status flags, EOF behavior, and descriptor inheritance.

Dependencies and integration points: Depends on LTP pipe/fcntl/safe I/O helpers, temporary processes, optional resource-limit changes, and blocking/nonblocking pipe semantics. Direct include dependencies include `unistd.h`, `signal.h`, `sys/wait.h`, `errno.h`, `test.h`, `tso_safe_macros.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TBROK`, `TERRNO`, `TFAIL`, `TPASS`, `TST_TOTAL`; checks errno values `EINTR`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe09.c -->
