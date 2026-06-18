<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl06_execve.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl06_execve.c

Purpose: Companion exec target for `prctl06.c`; it observes process attributes across exec so the parent can validate prctl inheritance semantics.

Important APIs/types/functions: includes `prctl06.h`; defines `main`.

Control flow centers on `main`.

State and persistence behavior: Runtime state is process attributes manipulated by `prctl()`, including name strings, dumpability, death signal, timer slack, seccomp, no-new-privs, and speculation/THP controls depending on the case.

Dependencies and integration points: Depends on Linux `prctl()` option availability, LTP capability/namespace/seccomp helpers, child exec helpers, and architecture/kernel feature probes. Direct include dependencies include `prctl06.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_NO_DEFAULT_MAIN`, `TST_RET`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl06_execve.c -->
