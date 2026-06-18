<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace11.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace11.c

Purpose: Before kernel 2.6.26 we could not trace init(1) process and ptrace() would fail with EPERM. This case just checks whether we can trace init(1) process successfully. Wait until tracee is stopped by SIGSTOP otherwise detach will fail with ESRCH.

Important APIs/types/functions: includes `errno.h`, `signal.h`, `sys/wait.h`, `pwd.h`, `stdlib.h`, `sys/ptrace.h`, `tst_test.h`; exercises `ptrace`; defines `verify_ptrace`; uses flags/constants `PTRACE_ATTACH`, `PTRACE_DETACH`.

Control flow centers on `verify_ptrace`. The `struct tst_test` registration wires `.test_all`, `.needs_root` into the LTP runner. Error-path expectations include `EPERM`, `ESRCH`.

State and persistence behavior: Runtime state is tracer/tracee relationship, stopped child tasks, ptrace request-specific registers or memory, and permission restrictions such as root-only attach.

Dependencies and integration points: Depends on ptrace request constants, fork/vfork stopped children, wait status handling, root permissions for attach cases, and architecture-specific register layouts. Direct include dependencies include `errno.h`, `signal.h`, `sys/wait.h`, `pwd.h`, `stdlib.h`, `sys/ptrace.h`.

Risks and test signals: Ptrace tests are privilege-, LSM-, Yama-, and architecture-sensitive; wait-state synchronization is critical to avoid ESRCH or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_RET`, `TTERRNO`; checks errno values `EPERM`, `ESRCH`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace11.c -->
