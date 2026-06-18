<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl06.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl06.h

Purpose: Shared constants and helpers for the `prctl06` no-new-privs/seccomp exec tests.

Important APIs/types/functions: includes `errno.h`, `stdio.h`, `stdlib.h`, `sys/prctl.h`, `pwd.h`, `sys/types.h`, `unistd.h`, `lapi/prctl.h`; defines `check_no_new_privs`; touches `prctl`; uses constants/macros such as `PR_GET_NO_NEW_PRIVS`, `TFAIL`, `TPASS`, `TST_ASSERT_FILE_INT`, `TST_RET`.

Control flow: this file is consumed at compile time by sibling tests; any inline or fallback functions normalize missing libc/kernel interfaces before the test bodies run.

State and persistence behavior: Runtime state is process attributes manipulated by `prctl()`, including name strings, dumpability, death signal, timer slack, seccomp, no-new-privs, and speculation/THP controls depending on the case.

Dependencies and integration points: Depends on Linux `prctl()` option availability, LTP capability/namespace/seccomp helpers, child exec helpers, and architecture/kernel feature probes. Direct include dependencies include `errno.h`, `stdio.h`, `stdlib.h`, `sys/prctl.h`, `pwd.h`, `sys/types.h`.

Risks and test signals: fallback wrappers must match the real syscall ABI exactly; otherwise sibling tests can pass compile but exercise the wrong argument layout. Signals are compile success and correct behavior in the consuming tests.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl06.h -->
