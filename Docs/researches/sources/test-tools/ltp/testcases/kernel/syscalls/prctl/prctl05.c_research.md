<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl05.c

Purpose: Test PR_GET_NAME and PR_SET_NAME of prctl(2). - Set the name of the calling thread, the name can be up to 16 bytes long, including the terminating null byte. If exceeds 16 bytes, the string is silently truncated. - Return the name of the calling thread, the buffer should allow space for up to 16 bytes, the returned string will be null-terminated. - Check /proc/self/task/[tid]/comm and /proc/self/comm name whether matches the thread name.

Important APIs/types/functions: includes `sys/prctl.h`, `string.h`, `stdio.h`, `tst_test.h`, `lapi/syscalls.h`, `lapi/prctl.h`; exercises `prctl`, `raw syscall path`; defines `verify_prctl`; uses flags/constants `PR_GET_NAME`, `PR_SET_NAME`.

Control flow centers on `verify_prctl`. The `struct tst_test` registration wires `.test`, `.tcnt` into the LTP runner. Named case hints include `prctl05_test`, `prctl05_test_xxxxx`.

State and persistence behavior: Runtime state is process attributes manipulated by `prctl()`, including name strings, dumpability, death signal, timer slack, seccomp, no-new-privs, and speculation/THP controls depending on the case.

Dependencies and integration points: Depends on Linux `prctl()` option availability, LTP capability/namespace/seccomp helpers, child exec helpers, and architecture/kernel feature probes. Direct include dependencies include `sys/prctl.h`, `string.h`, `stdio.h`, `tst_test.h`, `lapi/syscalls.h`, `lapi/prctl.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_ASSERT_STR`, `TST_RET`, `TTERRNO`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl05.c -->
