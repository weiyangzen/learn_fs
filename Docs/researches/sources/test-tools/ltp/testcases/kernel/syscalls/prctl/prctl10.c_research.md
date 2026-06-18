<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl10.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl10.c

Purpose: Basic test to test behaviour of PR_GET_TSC and PR_SET_TSC. Set the state of the flag determining whether the timestamp counter can be read by the process. - Pass PR_TSC_ENABLE to arg2 to allow it to be read. - Pass PR_TSC_SIGSEGV to arg2 to generate a SIGSEGV when read. We cannot use "=A", since this would use %rax on x86_64

Important APIs/types/functions: includes `sys/prctl.h`, `string.h`, `stdio.h`, `stdlib.h`, `tst_test.h`, `lapi/prctl.h`; exercises `prctl`, `read`; defines `expected_status`, `verify_prctl`; uses flags/constants `PR_GET_TSC`, `PR_SET_TSC`, `PR_TSC_ENABLE`, `PR_TSC_SIGSEGV`.

Control flow centers on `expected_status`, `verify_prctl`. The `struct tst_test` registration wires `.forks_child`, `.test`, `.tcnt` into the LTP runner. Named case hints include `x86`.

State and persistence behavior: Runtime state is process attributes manipulated by `prctl()`, including name strings, dumpability, death signal, timer slack, seccomp, no-new-privs, and speculation/THP controls depending on the case.

Dependencies and integration points: Depends on Linux `prctl()` option availability, LTP capability/namespace/seccomp helpers, child exec helpers, and architecture/kernel feature probes. Direct include dependencies include `sys/prctl.h`, `string.h`, `stdio.h`, `stdlib.h`, `tst_test.h`, `lapi/prctl.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_EXP_PASS_SILENT`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl10.c -->
