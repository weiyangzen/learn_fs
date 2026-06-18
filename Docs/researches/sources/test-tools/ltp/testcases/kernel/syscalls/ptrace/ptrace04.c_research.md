<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace04.c

Purpose: make sure PEEKUSER matches GETREGS first compare register states when execl() syscall starts then compare register states after execl() syscall finishes

Important APIs/types/functions: includes `errno.h`, `stdbool.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `sys/ptrace.h`, `test.h`, `spawn_ptrace_child.h`; exercises `ptrace`; defines `cleanup`, `compare_registers`, `main`; uses flags/constants `PTRACE_GETREGS`, `PTRACE_KILL`, `PTRACE_PEEKUSER`, `PTRACE_SYSCALL`.

Control flow centers on `cleanup`, `compare_registers`, `main`. Named case hints include `PT_`.

State and persistence behavior: Runtime state is tracer/tracee relationship, stopped child tasks, ptrace request-specific registers or memory, and permission restrictions such as root-only attach.

Dependencies and integration points: Depends on ptrace request constants, fork/vfork stopped children, wait status handling, root permissions for attach cases, and architecture-specific register layouts. Direct include dependencies include `errno.h`, `stdbool.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `sys/ptrace.h`.

Risks and test signals: Ptrace tests are privilege-, LSM-, Yama-, and architecture-sensitive; wait-state synchronization is critical to avoid ESRCH or false failures. Test signals: reports through `TCONF`, `TERRNO`, `TFAIL`, `TINFO`, `TPASS`, `TST_TOTAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace04.c -->
