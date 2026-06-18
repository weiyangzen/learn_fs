<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrandom/getrandom02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getrandom/getrandom02.c

Purpose: Calls getrandom(2), checks that the buffer is filled with random bytes and expects success.

Important APIs/types/functions: includes `tst_test.h`, `lapi/getrandom.h`, `lapi/syscalls.h`; touches `getrandom`, `raw syscall path`; defines `check_content`, `verify_getrandom`; uses LTP safe helpers such as `SAFE_FILE_SCANF`.

Control flow centers on `check_content`, `verify_getrandom`. The `struct tst_test` registration wires `.tcnt`, `.test` into the LTP runner. Error-path assertions cover `EAGAIN`.

State and persistence behavior: Runtime state is kernel randomness/entropy availability and caller buffers filled by getrandom.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`, `lapi/getrandom.h`, `lapi/syscalls.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TFAIL`, `TPASS`, `TST_ERR`, `TST_RET`. Expected errno values include `EAGAIN`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrandom/getrandom02.c -->
