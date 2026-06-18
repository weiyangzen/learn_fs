<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace03.c

Purpose: AUTHOR: Saji Kumar.V.R <saji.kumar@wipro.com> 1) ptrace() returns -1 and sets errno to ESRCH if process with specified pid does not exist. 2) ptrace() returns -1 and sets errno to EPERM if we are trying to trace a process which is already been traced

Important APIs/types/functions: includes `errno.h`, `signal.h`, `sys/wait.h`, `pwd.h`, `stdlib.h`, `sys/ptrace.h`, `tst_test.h`; exercises `ptrace`; defines `verify_ptrace`, `setup`; uses flags/constants `PTRACE_ATTACH`, `PTRACE_TRACEME`.

Control flow centers on `verify_ptrace`, `setup`. The `struct tst_test` registration wires `.test`, `.tcnt`, `.setup`, `.forks_child` into the LTP runner. Error-path expectations include `EPERM`, `ESRCH`.

State and persistence behavior: Runtime state is tracer/tracee relationship, stopped child tasks, ptrace request-specific registers or memory, and permission restrictions such as root-only attach.

Dependencies and integration points: Depends on ptrace request constants, fork/vfork stopped children, wait status handling, root permissions for attach cases, and architecture-specific register layouts. Direct include dependencies include `errno.h`, `signal.h`, `sys/wait.h`, `pwd.h`, `stdlib.h`, `sys/ptrace.h`.

Risks and test signals: Ptrace tests are privilege-, LSM-, Yama-, and architecture-sensitive; wait-state synchronization is critical to avoid ESRCH or false failures. Test signals: reports through `TFAIL`, `TINFO`, `TPASS`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EPERM`, `ESRCH`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace03.c -->
