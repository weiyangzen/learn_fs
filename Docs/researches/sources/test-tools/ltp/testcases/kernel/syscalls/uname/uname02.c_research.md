<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/uname/uname02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/uname/uname02.c

Purpose: Basic test for uname(): Calling uname() with invalid buf got EFAULT.

Important APIs/types/functions: includes `errno.h`, `sys/utsname.h`, `tst_test.h`; exercises `uname`; defines `verify_uname`, `setup`; uses constants `EFAULT`.

Control flow centers on `verify_uname`, `setup`. The `struct tst_test` registration wires `.test_all`, `.setup` into the runner. Error-path expectations include `EFAULT`.

State and persistence behavior: Runtime state is kernel utsname data and architecture/personality-dependent field length handling.

Dependencies and integration points: Depends on libc `uname()`, personality flags for old-uts behavior, and bad-address helpers for EFAULT coverage. Direct include dependencies include `errno.h`, `sys/utsname.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TST_EXP_FAIL`; checks errno values `EFAULT`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/uname/uname02.c -->
