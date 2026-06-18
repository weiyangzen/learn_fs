<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace09.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace09.c

Purpose: CVE-2018-8897 Test that the MOV SS instruction touching a ptrace watchpoint followed by INT3 breakpoint is handled correctly by the kernel. Kernel crash fixed in: commit d8ba61ba58c88d5207c1ba2f7d9a2280e7d03be9 Date: Thu Jul 23 15:37:48 2015 -0700 x86/entry/64: Don't use IST entry for #BP stack wait for SIGCONT from parent Main process terminated by tst_brk() with child still paused

Important APIs/types/functions: includes `stdlib.h`, `stddef.h`, `sys/ptrace.h`, `sys/user.h`, `signal.h`, `tst_test.h`; exercises `ptrace`; defines `child_main`, `run`, `cleanup`; uses flags/constants `PTRACE_CONT`, `PTRACE_POKEUSER`, `PTRACE_TRACEME`.

Control flow centers on `child_main`, `run`, `cleanup`. The `struct tst_test` registration wires `.test_all`, `.cleanup`, `.forks_child` into the LTP runner. Named case hints include `x86`, `linux-git`, `CVE`.

State and persistence behavior: Runtime state is tracer/tracee relationship, stopped child tasks, ptrace request-specific registers or memory, and permission restrictions such as root-only attach.

Dependencies and integration points: Depends on ptrace request constants, fork/vfork stopped children, wait status handling, root permissions for attach cases, and architecture-specific register layouts. Direct include dependencies include `stdlib.h`, `stddef.h`, `sys/ptrace.h`, `sys/user.h`, `signal.h`, `tst_test.h`.

Risks and test signals: Ptrace tests are privilege-, LSM-, Yama-, and architecture-sensitive; wait-state synchronization is critical to avoid ESRCH or false failures. Test signals: reports through `TBROK`, `TPASS`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace09.c -->
