<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace06.c

Purpose: Check out-of-bound/unaligned addresses given to - {PEEK,POKE}{DATA,TEXT,USER} - {GET,SET}{,FG}REGS - {GET,SET}SIGINFO this should be sizeof(struct user), but that info is only found in the kernel asm/user.h which is not exported to userspace.

Important APIs/types/functions: includes `stdlib.h`, `sys/ptrace.h`, `tst_test.h`; exercises `ptrace`; defines `child`, `run`; uses flags/constants `PTRACE_CONT`, `PTRACE_GETFGREGS`, `PTRACE_GETREGS`, `PTRACE_GETSIGINFO`, `PTRACE_PEEKDATA`, `PTRACE_PEEKTEXT`, `PTRACE_PEEKUSER`, `PTRACE_POKEDATA`, `PTRACE_POKETEXT`, `PTRACE_POKEUSER`, `PTRACE_SETFGREGS`, `PTRACE_SETREGS`, `PTRACE_SETSIGINFO`, `PTRACE_TRACEME`.

Control flow centers on `child`, `run`. The `struct tst_test` registration wires `.test_all`, `.forks_child` into the LTP runner. Error-path expectations include `EFAULT`, `EIO`.

State and persistence behavior: Runtime state is tracer/tracee relationship, stopped child tasks, ptrace request-specific registers or memory, and permission restrictions such as root-only attach.

Dependencies and integration points: Depends on ptrace request constants, fork/vfork stopped children, wait status handling, root permissions for attach cases, and architecture-specific register layouts. Direct include dependencies include `stdlib.h`, `sys/ptrace.h`, `tst_test.h`.

Risks and test signals: Ptrace tests are privilege-, LSM-, Yama-, and architecture-sensitive; wait-state synchronization is critical to avoid ESRCH or false failures. Test signals: reports through `TBROK`, `TST_EXP_FAIL_ARR`; checks errno values `EFAULT`, `EIO`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace06.c -->
