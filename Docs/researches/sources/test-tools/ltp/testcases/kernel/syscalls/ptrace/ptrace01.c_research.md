<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace01.c

Purpose: Ported to new library: Jorik Cronenberg <jcronenberg@suse.de> Test the functionality of ptrace() for PTRACE_TRACEME in combination with PTRACE_KILL and PTRACE_CONT requests. Forked child does ptrace(PTRACE_TRACEME, ...). Then a signal is delivered to the child and verified that parent is notified via wait(). Afterwards parent does ptrace(PTRACE_KILL, ..)/ptrace(PTRACE_CONT, ..) and then parent does wait() for child to finish. Test passes if child exits with SIGKILL for PTRACE_KILL. Test passes if child exits normally for PTRACE_CONT. Testing two cases for each: 1) child ignore SIGUSR2 signal 2) using a signal han

Important APIs/types/functions: includes `stdlib.h`, `errno.h`, `signal.h`, `sys/wait.h`, `sys/ptrace.h`, `tst_test.h`; exercises `ptrace`; defines `child_handler`, `parent_handler`, `do_child`, `run`; uses flags/constants `PTRACE_CONT`, `PTRACE_KILL`, `PTRACE_TRACEME`.

Control flow centers on `child_handler`, `parent_handler`, `do_child`, `run`. The `struct tst_test` registration wires `.test`, `.tcnt`, `.forks_child` into the LTP runner.

State and persistence behavior: Runtime state is tracer/tracee relationship, stopped child tasks, ptrace request-specific registers or memory, and permission restrictions such as root-only attach.

Dependencies and integration points: Depends on ptrace request constants, fork/vfork stopped children, wait status handling, root permissions for attach cases, and architecture-specific register layouts. Direct include dependencies include `stdlib.h`, `errno.h`, `signal.h`, `sys/wait.h`, `sys/ptrace.h`, `tst_test.h`.

Risks and test signals: Ptrace tests are privilege-, LSM-, Yama-, and architecture-sensitive; wait-state synchronization is critical to avoid ESRCH or false failures. Test signals: reports through `TERRNO`, `TFAIL`, `TINFO`, `TPASS`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/ptrace01.c -->
