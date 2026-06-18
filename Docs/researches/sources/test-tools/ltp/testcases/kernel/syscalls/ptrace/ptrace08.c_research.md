<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace08.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace08.c

Purpose: CVE-2018-1000199 Test error handling when ptrace(POKEUSER) modified x86 debug registers even when the call returned error. When the bug was present we could create breakpoint in the kernel code, which shoudn't be possible at all. The original CVE caused a kernel crash by setting a breakpoint on do_debug kernel function which, when triggered, caused an infinite loop. However we do not have to crash the kernel in order to assert if kernel has been fixed or not. On newer kernels all we have to do is to try to set a breakpoint, on any kernel address, then read it back and check if the value has been set or not. The o

Important APIs/types/functions: includes `stdlib.h`, `stdio.h`, `stddef.h`, `sys/ptrace.h`, `sys/user.h`, `signal.h`, `tst_test.h`, `tst_safe_stdio.h`; exercises `ptrace`, `read`, `write`; defines `child_main`, `ptrace_try_kern_addr`, `run`, `cleanup`; uses flags/constants `PTRACE_ATTACH`, `PTRACE_DETACH`, `PTRACE_PEEKUSER`, `PTRACE_POKEUSER`.

Control flow centers on `child_main`, `ptrace_try_kern_addr`, `run`, `cleanup`. The `struct tst_test` registration wires `.test_all`, `.cleanup`, `.forks_child` into the LTP runner. Named case hints include `x86`, `linux-git`, `CVE`. Error-path expectations include `EINVAL`.

State and persistence behavior: Runtime state is tracer/tracee relationship, stopped child tasks, ptrace request-specific registers or memory, and permission restrictions such as root-only attach.

Dependencies and integration points: Depends on ptrace request constants, fork/vfork stopped children, wait status handling, root permissions for attach cases, and architecture-specific register layouts. Direct include dependencies include `stdlib.h`, `stdio.h`, `stddef.h`, `sys/ptrace.h`, `sys/user.h`, `signal.h`.

Risks and test signals: Ptrace tests are privilege-, LSM-, Yama-, and architecture-sensitive; wait-state synchronization is critical to avoid ESRCH or false failures. Test signals: reports through `TBROK`, `TFAIL`, `TINFO`, `TPASS`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EINVAL`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace08.c -->
