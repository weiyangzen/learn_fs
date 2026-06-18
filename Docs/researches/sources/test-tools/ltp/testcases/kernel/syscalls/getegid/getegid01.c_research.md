<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getegid/getegid01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getegid/getegid01.c

Purpose: William Roske, Dave Fenner This test checks if getegid() returns the effective group id.

Important APIs/types/functions: includes `tst_test.h`, `compat_tst_16.h`; touches `getegid`; defines `run`; uses LTP safe helpers such as `SAFE_FILE_LINES_SCANF`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is the process effective group ID as reported by the kernel and, in some tests, cross-checked through proc or passwd-derived credentials.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`, `compat_tst_16.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TPASS`, `TST_EXP_EQ_LI`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getegid/getegid01.c -->
