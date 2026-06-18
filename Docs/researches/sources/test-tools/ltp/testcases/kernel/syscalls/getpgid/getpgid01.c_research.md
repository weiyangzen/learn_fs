<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getpgid/getpgid01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getpgid/getpgid01.c

Purpose: 07/2001 Ported by Wayne Boyer Verify the basic functionality of getpgid(2) syscall.

Important APIs/types/functions: includes `tst_test.h`; touches `getpgid`, `getpid`; defines `get_init_pgid`, `run`; uses LTP safe helpers such as `SAFE_FILE_SCANF`, `SAFE_FORK`.

Control flow centers on `get_init_pgid`, `run`. The `struct tst_test` registration wires `.test_all`, `.forks_child` into the LTP runner.

State and persistence behavior: Runtime state is process group membership for the current process, children, and invalid/unreferenced PIDs.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TST_EXP_EQ_LI`, `TST_EXP_PID`, `TST_RET`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getpgid/getpgid01.c -->
