<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace05.c

Purpose: This test ptraces itself as per arbitrarily specified signals, over 0 to SIGRTMAX range. All other processes should be stopped.

Important APIs/types/functions: includes `stdlib.h`, `sys/ptrace.h`, `lapi/signal.h`, `tst_test.h`; exercises `ptrace`; defines `test_signal`, `run`; uses flags/constants `PTRACE_CONT`, `PTRACE_TRACEME`.

Control flow centers on `test_signal`, `run`. The `struct tst_test` registration wires `.test_all`, `.forks_child` into the LTP runner.

State and persistence behavior: Runtime state is tracer/tracee relationship, stopped child tasks, ptrace request-specific registers or memory, and permission restrictions such as root-only attach.

Dependencies and integration points: Depends on ptrace request constants, fork/vfork stopped children, wait status handling, root permissions for attach cases, and architecture-specific register layouts. Direct include dependencies include `stdlib.h`, `sys/ptrace.h`, `lapi/signal.h`, `tst_test.h`.

Risks and test signals: Ptrace tests are privilege-, LSM-, Yama-, and architecture-sensitive; wait-state synchronization is critical to avoid ESRCH or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_EXP_PASS_SILENT`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace05.c -->
