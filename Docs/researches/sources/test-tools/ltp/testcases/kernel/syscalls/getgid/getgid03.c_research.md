<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getgid/getgid03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getgid/getgid03.c

Purpose: Ported by Wayne Boyer Testcase to check the basic functionality of getgid(). [Algorithm] For functionality test the return value from getgid() is compared to passwd entry.

Important APIs/types/functions: includes `pwd.h`, `tst_test.h`, `compat_tst_16.h`; touches `getgid`, `getuid`; defines `run`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is the process real group ID; setup may switch to a known test account/group before validation.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `pwd.h`, `tst_test.h`, `compat_tst_16.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TBROK`, `TFAIL`, `TPASS`, `TST_RET`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getgid/getgid03.c -->
