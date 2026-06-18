<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getcontext/getcontext01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getcontext/getcontext01.c

Purpose:  Basic test for getcontext(). Calls a getcontext() then jumps back with a setcontext().

Important APIs/types/functions: includes `config.h`, `tst_test.h`, `ucontext.h`; touches `getcontext`; defines `run`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is the user-space ucontext_t snapshot returned by getcontext.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `config.h`, `tst_test.h`, `ucontext.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TFAIL`, `TST_EXP_PASS`, `TST_TEST_TCONF`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getcontext/getcontext01.c -->
