<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrandom/getrandom04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getrandom/getrandom04.c

Purpose: Calls getrandom(2) after having limited the number of available file descriptors to 3 and expects success.

Important APIs/types/functions: includes `sys/resource.h`, `tst_test.h`, `lapi/getrandom.h`, `lapi/syscalls.h`; touches `getrandom`, `raw syscall path`; defines `verify_getrandom`; uses LTP safe helpers such as `SAFE_GETRLIMIT`, `SAFE_SETRLIMIT`.

Control flow centers on `verify_getrandom`. The `struct tst_test` registration wires `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is kernel randomness/entropy availability and caller buffers filled by getrandom.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `sys/resource.h`, `tst_test.h`, `lapi/getrandom.h`, `lapi/syscalls.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TFAIL`, `TPASS`, `TST_RET`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrandom/getrandom04.c -->
