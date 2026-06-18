<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getcwd/getcwd01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getcwd/getcwd01.c

Purpose: DESCRIPTION Testcase to test that getcwd(2) sets errno correctly. 1) getcwd(2) fails if buf points to a bad address. 2) getcwd(2) fails if the size is invalid. 3) getcwd(2) fails if the size is set to 0. 4) getcwd(2) fails if the size is set to 1. 5) getcwd(2) fails if buf points to NULL and the size is set to 1. Expected Result: 1) getcwd(2) should return NULL and set errno to EFAULT. 2) getcwd(2) should return NULL and set errno to EFAULT. 3) getcwd(2) should return NULL and set errno to ERANGE. 4) getcwd(2) shou

Important APIs/types/functions: includes `errno.h`, `unistd.h`, `limits.h`, `tst_test.h`, `lapi/syscalls.h`; touches `getcwd`, `raw syscall path`; defines `verify_getcwd`.

Control flow centers on `verify_getcwd`. The `struct tst_test` registration wires `.tcnt`, `.test` into the LTP runner. Error-path assertions cover `EFAULT`, `ERANGE`.

State and persistence behavior: Runtime state is the process current working directory and path dentries; several tests mutate directories, symlinks, or renamed paths while checking returned buffers and errors.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `errno.h`, `unistd.h`, `limits.h`, `tst_test.h`, `lapi/syscalls.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TST_EXP_FAIL2`. Expected errno values include `EFAULT`, `ERANGE`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getcwd/getcwd01.c -->
