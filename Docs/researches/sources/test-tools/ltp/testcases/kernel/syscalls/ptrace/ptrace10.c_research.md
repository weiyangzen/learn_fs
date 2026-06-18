<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace10.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace10.c

Purpose: After fix for CVE-2018-1000199 (see ptrace08.c) subsequent calls to POKEUSER for x86 debug registers were ignored silently. This is a regression test for commit: commit bd14406b78e6daa1ea3c1673bda1ffc9efdeead0 Date: Mon Aug 27 11:12:25 2018 +0200 perf/hw_breakpoint: Modify breakpoint even if the new attr has disabled set Main process terminated by tst_brk() with child still paused

Important APIs/types/functions: includes `stdlib.h`, `stdio.h`, `stddef.h`, `sys/ptrace.h`, `sys/user.h`, `signal.h`, `tst_test.h`; exercises `ptrace`; defines `child_main`, `run`, `cleanup`; uses flags/constants `PTRACE_ATTACH`, `PTRACE_DETACH`, `PTRACE_PEEKUSER`, `PTRACE_POKEUSER`, `PTRACE_POKEUSR`.

Control flow centers on `child_main`, `run`, `cleanup`. The `struct tst_test` registration wires `.test_all`, `.cleanup`, `.forks_child` into the LTP runner. Named case hints include `x86`, `linux-git`.

State and persistence behavior: Runtime state is tracer/tracee relationship, stopped child tasks, ptrace request-specific registers or memory, and permission restrictions such as root-only attach.

Dependencies and integration points: Depends on ptrace request constants, fork/vfork stopped children, wait status handling, root permissions for attach cases, and architecture-specific register layouts. Direct include dependencies include `stdlib.h`, `stdio.h`, `stddef.h`, `sys/ptrace.h`, `sys/user.h`, `signal.h`.

Risks and test signals: Ptrace tests are privilege-, LSM-, Yama-, and architecture-sensitive; wait-state synchronization is critical to avoid ESRCH or false failures. Test signals: reports through `TBROK`, `TFAIL`, `TPASS`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace10.c -->
