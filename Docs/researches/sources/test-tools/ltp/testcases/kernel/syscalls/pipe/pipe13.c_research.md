<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe13.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe13.c

Purpose: Test Description: This case is designed to test whether pipe can wakeup all readers when last writer closes. This is also a regression test for commit 6551d5c56eb0 ("pipe: make sure to wake up everybody when the last reader/writer closes"). This bug was introduced by commit 0ddad21d3e99 ("pipe: use exclusive waits when reading or writing").

Important APIs/types/functions: includes `unistd.h`, `sys/types.h`, `sys/wait.h`, `stdlib.h`, `tst_test.h`; exercises `pipe`, `waitpid`, `read`; defines `do_child`, `verify_pipe`.

Control flow centers on `do_child`, `verify_pipe`. The `struct tst_test` registration wires `.test`, `.tcnt`, `.forks_child` into the LTP runner. Named case hints include `linux-git`.

State and persistence behavior: Runtime state is anonymous pipe file descriptors, pipe buffer contents/capacity, blocking and nonblocking status flags, EOF behavior, and descriptor inheritance.

Dependencies and integration points: Depends on LTP pipe/fcntl/safe I/O helpers, temporary processes, optional resource-limit changes, and blocking/nonblocking pipe semantics. Direct include dependencies include `unistd.h`, `sys/types.h`, `sys/wait.h`, `stdlib.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TBROK`, `TERRNO`, `TFAIL`, `TINFO`, `TPASS`, `TST_CHECKPOINT_WAIT`, `TST_CHECKPOINT_WAKE`, `TST_PROCESS_STATE_WAIT`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe13.c -->
