<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe02.c

Purpose: Check that if a child has a "broken pipe", this information is transmitted to the waiting parent.

Important APIs/types/functions: includes `errno.h`, `string.h`, `unistd.h`, `stdlib.h`, `sys/wait.h`, `tst_test.h`; exercises `pipe`, `read`, `write`; defines `do_child`, `verify_pipe`.

Control flow centers on `do_child`, `verify_pipe`. The `struct tst_test` registration wires `.forks_child`, `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is anonymous pipe file descriptors, pipe buffer contents/capacity, blocking and nonblocking status flags, EOF behavior, and descriptor inheritance.

Dependencies and integration points: Depends on LTP pipe/fcntl/safe I/O helpers, temporary processes, optional resource-limit changes, and blocking/nonblocking pipe semantics. Direct include dependencies include `errno.h`, `string.h`, `unistd.h`, `stdlib.h`, `sys/wait.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_CHECKPOINT_WAIT`, `TST_CHECKPOINT_WAKE`, `TST_RET`, `TTERRNO`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe02.c -->
