<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace02.c

Purpose: Ptrace register-consistency test that compares `PTRACE_PEEKUSER` register values with `PTRACE_GETREGS` around an `execl()` syscall stop.

Important APIs/types/functions: includes `errno.h`, `signal.h`, `sys/wait.h`, `pwd.h`, `stdlib.h`, `sys/ptrace.h`, `tst_test.h`; exercises `pause`, `ptrace`; defines `verify_ptrace`, `setup`; uses flags/constants `PTRACE_ATTACH`.

Control flow centers on `verify_ptrace`, `setup`. The `struct tst_test` registration wires `.setup`, `.test_all`, `.forks_child`, `.needs_root` into the LTP runner. Error-path expectations include `EPERM`.

State and persistence behavior: Runtime state is tracer/tracee relationship, stopped child tasks, ptrace request-specific registers or memory, and permission restrictions such as root-only attach.

Dependencies and integration points: Depends on ptrace request constants, fork/vfork stopped children, wait status handling, root permissions for attach cases, and architecture-specific register layouts. Direct include dependencies include `errno.h`, `signal.h`, `sys/wait.h`, `pwd.h`, `stdlib.h`, `sys/ptrace.h`.

Risks and test signals: Ptrace tests are privilege-, LSM-, Yama-, and architecture-sensitive; wait-state synchronization is critical to avoid ESRCH or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EPERM`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace02.c -->
