<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/personality/personality02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/personality/personality02.c

Purpose: This test checks if select() timeout is not updated when personality with STICKY_TIMEOUTS is used.

Important APIs/types/functions: includes `tst_test.h`, `lapi/personality.h`, `sys/select.h`; exercises `personality`; defines `run`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is the process execution-domain/personality word, including architecture-specific flags that must be restored after each test.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`, `lapi/personality.h`, `sys/select.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TBROK`, `TERRNO`, `TST_EXP_EQ_LI`, `TST_RET`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/personality/personality02.c -->
