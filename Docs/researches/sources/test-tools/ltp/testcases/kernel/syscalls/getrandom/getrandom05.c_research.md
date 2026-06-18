<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrandom/getrandom05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getrandom/getrandom05.c

Purpose:  Verify that getrandom(2) fails with - EFAULT when buf address is outside the accessible address space - EINVAL when flag is invalid

Important APIs/types/functions: includes `tst_test.h`, `lapi/getrandom.h`, `getrandom_var.h`; touches `getrandom`; defines `setup`, `verify_getrandom`.

Control flow centers on `setup`, `verify_getrandom`. The `struct tst_test` registration wires `.tcnt`, `.test`, `.test_variants`, `.setup` into the LTP runner. Error-path assertions cover `EFAULT`, `EINVAL`.

State and persistence behavior: Runtime state is kernel randomness/entropy availability and caller buffers filled by getrandom.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`, `lapi/getrandom.h`, `getrandom_var.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TCONF`, `TST_EXP_FAIL2`. Expected errno values include `EFAULT`, `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrandom/getrandom05.c -->
