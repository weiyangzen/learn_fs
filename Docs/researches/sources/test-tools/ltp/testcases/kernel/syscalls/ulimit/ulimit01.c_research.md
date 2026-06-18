<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ulimit/ulimit01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ulimit/ulimit01.c

Purpose: Tests the basic functionality of :manpage:`ulimit(3)` with UL_GETFSIZE and UL_SETFSIZE.

Important APIs/types/functions: includes `ulimit.h`, `tst_test.h`; exercises `ulimit`; defines `run`; uses constants `UL_GETFSIZE`, `UL_SETFSIZE`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test_all` into the runner.

State and persistence behavior: Runtime state is the process file-size limit manipulated through the legacy libc `ulimit()` interface.

Dependencies and integration points: Depends on libc `ulimit()` and process resource limit state. Direct include dependencies include `ulimit.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TST_EXP_POSITIVE`, `TST_PASS`, `TST_RET`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ulimit/ulimit01.c -->
