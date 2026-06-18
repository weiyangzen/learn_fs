<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl01.c

Purpose: Basic test for PR_SET_PDEATHSIG/PR_GET_PDEATHSIG Use PR_SET_PDEATHSIG to set SIGUSR2 signal and PR_GET_PDEATHSIG should receive this signal.

Important APIs/types/functions: includes `errno.h`, `signal.h`, `sys/prctl.h`, `tst_test.h`; exercises `prctl`; defines `verify_prctl`; uses flags/constants `PR_GET_PDEATHSIG`, `PR_SET_PDEATHSIG`.

Control flow centers on `verify_prctl`. The `struct tst_test` registration wires `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is process attributes manipulated by `prctl()`, including name strings, dumpability, death signal, timer slack, seccomp, no-new-privs, and speculation/THP controls depending on the case.

Dependencies and integration points: Depends on Linux `prctl()` option availability, LTP capability/namespace/seccomp helpers, child exec helpers, and architecture/kernel feature probes. Direct include dependencies include `errno.h`, `signal.h`, `sys/prctl.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_RET`, `TTERRNO`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl01.c -->
