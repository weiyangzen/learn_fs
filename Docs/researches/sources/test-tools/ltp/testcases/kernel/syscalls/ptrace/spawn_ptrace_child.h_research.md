<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/spawn_ptrace_child.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/spawn_ptrace_child.h

Purpose: Reusable legacy ptrace helper that vforks a child, asks it to `PTRACE_TRACEME`, execs itself in child mode, and exposes `pid`, `vptrace()`, and request-name helpers to ptrace tests.

Important APIs/types/functions: includes `spawn_ptrace_child.c`, `errno.h`, `signal.h`, `stdbool.h`, `string.h`, `unistd.h`, `sys/ptrace.h`, `sys/wait.h`; defines `make_a_baby`; touches `ptrace`, `vfork`, `execlp`; uses constants/macros such as `PTRACE_GETFGREGS`, `PTRACE_GETREGS`, `PTRACE_GETSIGINFO`, `PTRACE_SETFGREGS`, `PTRACE_SETREGS`, `PTRACE_SETSIGINFO`, `PTRACE_TRACEME`, `TBROK`, `TERRNO`, `TFAIL`.

Control flow: this file is consumed at compile time by sibling tests; any inline or fallback functions normalize missing libc/kernel interfaces before the test bodies run.

State and persistence behavior: Runtime state is tracer/tracee relationship, stopped child tasks, ptrace request-specific registers or memory, and permission restrictions such as root-only attach.

Dependencies and integration points: Depends on ptrace request constants, fork/vfork stopped children, wait status handling, root permissions for attach cases, and architecture-specific register layouts. Direct include dependencies include `spawn_ptrace_child.c`, `errno.h`, `signal.h`, `stdbool.h`, `string.h`, `unistd.h`.

Risks and test signals: fallback wrappers must match the real syscall ABI exactly; otherwise sibling tests can pass compile but exercise the wrong argument layout. Signals are compile success and correct behavior in the consuming tests.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ptrace/spawn_ptrace_child.h -->
