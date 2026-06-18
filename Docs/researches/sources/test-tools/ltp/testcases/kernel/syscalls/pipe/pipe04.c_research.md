<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe04.c

Purpose: Legacy pipe test checking that writer children blocked or busy writing to a pipe remain killable and are reaped by the parent.

Important APIs/types/functions: includes `unistd.h`, `errno.h`, `signal.h`, `sys/types.h`, `sys/wait.h`, `test.h`, `tso_safe_macros.h`; exercises `pipe`, `fork`, `waitpid`, `read`, `write`; defines `setup`, `cleanup`, `c1func`, `c2func`, `alarmfunc`, `do_read`, `main`.

Control flow centers on `setup`, `cleanup`, `c1func`, `c2func`, `alarmfunc`, `do_read`, `main`. Error-path expectations include `EINTR`.

State and persistence behavior: Runtime state is anonymous pipe file descriptors, pipe buffer contents/capacity, blocking and nonblocking status flags, EOF behavior, and descriptor inheritance.

Dependencies and integration points: Depends on LTP pipe/fcntl/safe I/O helpers, temporary processes, optional resource-limit changes, and blocking/nonblocking pipe semantics. Direct include dependencies include `unistd.h`, `errno.h`, `signal.h`, `sys/types.h`, `sys/wait.h`, `test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TBROK`, `TERRNO`, `TFAIL`, `TPASS`, `TST_TOTAL`; checks errno values `EINTR`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe04.c -->
